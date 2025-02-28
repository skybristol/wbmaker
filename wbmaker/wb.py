import os
import requests
import pandas as pd
from urllib.parse import urlparse
from wikibaseintegrator.wbi_config import config as wbi_config
from wikibaseintegrator import WikibaseIntegrator, wbi_login
from wikibaseintegrator import datatypes, wbi_enums
import mwclient
from datetime import datetime
from dateutil.parser import parse as parse_date
import networkx as nx

class WB:
    def __init__(
        self, 
        cache_props: bool = True,
        is_bot: bool = True):

        # Check for required environment variables
        required_vars = {
            'WB_URL': 'Enter the base URL for the Wikibase instance: ',
            'WB_SPARQL_ENDPOINT': 'Enter the SPARQL endpoint for the Wikibase instance: ',
            'MEDIAWIKI_API': 'Enter the Mediawiki API URL for the Wikibase instance: ',
            'WB_BOT_USER_AGENT': 'Enter the user agent string to use in bot actions: '
        }

        for var, prompt in required_vars.items():
            if not os.environ.get(var):
                os.environ[var] = input(prompt)

        # Verify all required environment variables are set
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        if missing_vars:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

        # WikibaseIntegrator config
        wbi_config['SPARQL_ENDPOINT_URL'] = os.environ.get('WB_SPARQL_ENDPOINT')
        wbi_config['USER_AGENT'] = os.environ.get('WB_BOT_USER_AGENT')
        wbi_config['MEDIAWIKI_API_URL'] = os.environ.get('MEDIAWIKI_API')
        wbi_config['WIKIBASE_URL'] = os.environ.get('WB_URL')

        # Pass along key wikibaseintegrator objects for building workflows
        self.datatypes = datatypes
        self.wbi_enums = wbi_enums

        # Establish mwclient connection
        self.mw_site = mwclient.Site(
            self._get_domain(os.environ.get('WB_URL')), 
            path='/w/', 
            scheme='https', 
            clients_useragent=os.environ.get('WB_BOT_USER_AGENT')
        )

        # Establish authentication connection if bot credentials are provided
        if os.environ.get('WB_BOT_USER') and os.environ.get('WB_BOT_PASS'):
            self.login_instance = wbi_login.Login(
                user=os.environ.get('WB_BOT_USER'),
                password=os.environ.get('WB_BOT_PASS')
            )
            self.wbi = WikibaseIntegrator(login=self.login_instance, is_bot=is_bot)

            self.mw_site.login(username=os.environ.get('WB_BOT_USER'), password=os.environ.get('WB_BOT_PASS'))
        else:
            self.wbi = WikibaseIntegrator()

        if cache_props:
            self.props = self.property_map()
            
    def _get_domain(self, url):
        parsed_uri = urlparse(url)
        domain = '{uri.netloc}'.format(uri=parsed_uri)
        return domain

    def sparql_query(self, query: str, endpoint: str = None, output: str = 'dataframe'):
        if not endpoint:
            endpoint = wbi_config['SPARQL_ENDPOINT_URL']
        
        r = requests.get(
            endpoint, 
            params = {'format': 'json', 'query': query}
        )

        if r.status_code != 200:
            return

        try:
            json_results = r.json()
        except Exception as e:
            return None
        
        if not json_results['results']['bindings']:
            return None

        if output == 'raw':
            return json_results
        else:
            data_records = []
            var_names = json_results['head']['vars']

            for record in json_results['results']['bindings']:
                data_record = {}
                for var_name in var_names:
                    data_record[var_name] = record[var_name]['value'] if var_name in record else None
                data_records.append(data_record)

            if output == 'dataframe':
                return pd.DataFrame(data_records)
            elif output == 'lookup':
                # Assumes first column contains identifier and second column contains label
                df = pd.DataFrame(data_records)
                df['lookup_value'] = df.iloc[:, 1]
                df['identifier'] = df.iloc[:, 0].apply(lambda x: x.split('/')[-1])
                return df[['lookup_value','identifier']].set_index('lookup_value').to_dict()['identifier']
            else:
                return data_records
    
    def property_map(self):
        q_props = """
        PREFIX wdt: <https://geokb.wikibase.cloud/prop/direct/>

        SELECT ?property ?propertyLabel ?dataType ?formatter_url
        WHERE {
        ?property a wikibase:Property ;
                  wikibase:propertyType ?dataType .
        OPTIONAL {
            ?property wdt:P26 ?formatter_url .
        }
        SERVICE wikibase:label { bd:serviceParam wikibase:language "en".}
        }
        """

        props = self.sparql_query(q_props)
        props['property'] = props['property'].str.split('/').str[-1]
        props['dataType'] = props['dataType'].str.split('#').str[-1]

        wbi_dtype_class_mapping = {
            'WikibaseItem': datatypes.Item,
            'WikibaseProperty': datatypes.Property,
            'String': datatypes.String,
            'ExternalId': datatypes.ExternalID,
            'Time': datatypes.Time,
            'Quantity': datatypes.Quantity,
            'Url': datatypes.URL,
            'Monolingualtext': datatypes.MonolingualText,
            'GlobeCoordinate': datatypes.GlobeCoordinate,
            'Math': datatypes.Math,
            'TabularData': datatypes.TabularData,
            'MusicalNotation': datatypes.MusicalNotation,
            'WikibaseLexeme': datatypes.Lexeme,
            'WikibaseForm': datatypes.Form,
            'WikibaseSense': datatypes.Sense,
            'GeoShape': datatypes.GeoShape,
            'CommonsMedia': datatypes.CommonsMedia
        }
        props['wbiClass'] = props['dataType'].map(wbi_dtype_class_mapping)

        return props.set_index('propertyLabel').to_dict(orient='index')

    def wb_dt(self, dt=datetime.now()):
        '''
        Converts a string (or datetime object) to a proper Wikibase datetime string
        '''
        if not isinstance(dt, datetime):
            try:
                dt = parse_date(dt)
            except:
                return None
        return dt.strftime("+%Y-%m-%dT%H:%M:%SZ").split('T')[0] + 'T00:00:00Z'

    def wd_path_analysis(self, wd_start, wd_lookup, wd_end='Q35120', alternate_path=False, max_paths=10):
        '''
        This function examines the subclass hierarchy of a Wikidata item to determine if a path exists to a target item.
        It returns two structures, one representing the shortest path and the other representing the path with the most local links. 
        that corresponds to the Wikidata entity ID via a same as relationship (or any type of mapping between the two).

        Parameters:
        wd_start (str): The Wikidata entity ID of the starting item
        wd_lookup (dict): A dictionary mapping Wikidata entity IDs to entity IDs in another Wikibase
        wd_end (str): The Wikidata entity ID of the target item (defaults to the high-level 'entity' class in Wikidata)
        '''
        start_node = f'http://www.wikidata.org/entity/{wd_start}'
        end_node = f'http://www.wikidata.org/entity/{wd_end}'

        q_wd = f"""
        PREFIX wd: <http://www.wikidata.org/entity/>
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>

        SELECT ?item ?itemLabel ?itemDescription 
        ?subclass_of ?subclass_ofLabel ?subclass_ofDescription
        ?next_subclass ?next_subclassLabel ?next_subclassDescription
        WHERE {{
            ?item wdt:P279* ?subclass_of .
            VALUES ?item {{ wd:{wd_start} }}
            ?subclass_of wdt:P279 ?next_subclass .
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        """ % {'item': wd_start}

        df = self.sparql_query(q_wd, endpoint='https://query.wikidata.org/sparql')
        if df is None:
            return None

        label_lookup = df.set_index('item')['itemLabel'].to_dict()
        label_lookup.update(df.set_index('subclass_of')['subclass_ofLabel'].to_dict())
        label_lookup.update(df.set_index('next_subclass')['next_subclassLabel'].to_dict())
        if end_node not in label_lookup or start_node not in label_lookup:
            return None
        
        description_lookup = df.set_index('item')['itemDescription'].to_dict()
        description_lookup.update(df.set_index('subclass_of')['subclass_ofDescription'].to_dict())
        description_lookup.update(df.set_index('next_subclass')['next_subclassDescription'].to_dict())

        G = nx.Graph()

        nodes = list(set(df['item'].to_list() + df['subclass_of'].to_list() + df['next_subclass'].to_list()))
        G.add_nodes_from(nodes)

        edges = list(df[['item','subclass_of']].to_records(index=False)) + list(df[['subclass_of','next_subclass']].to_records(index=False))
        G.add_edges_from(edges)

        shortest_path = nx.shortest_path(G, source=start_node, target=end_node)
        path_analysis = {
            'shortest_path': [
                {
                    'wd_entity': item,
                    'wd_label': label_lookup[item],
                    'wd_description': description_lookup[item],
                    'geokb_entity': wd_lookup.get(item, None)
                }
                for item in shortest_path
            ],
        }

        if alternate_path:
            path_analysis['alternate_path'] = []
            alternate_paths = []           

            for i, path in enumerate(nx.all_simple_paths(G, source=start_node, target=end_node)):
                if i >= max_paths:
                    break
                num_local_links = 0
                path_list = []
                for item in path:
                    wb_item = wd_lookup.get(item, None)
                    if wb_item:
                        num_local_links += 1
                    p = {
                        'wd_entity': item,
                        'wd_label': label_lookup[item],
                        'wd_description': description_lookup[item],
                        'geokb_entity': wb_item
                    }
                    path_list.append(p)
                if num_local_links > 1:
                    alternate_paths.append((num_local_links, path_list))
            
            if alternate_paths:
                alternate_paths.sort(key=lambda x: x[0], reverse=True)
                path_analysis['alternate_path'] = alternate_paths[0][1]

        return path_analysis
