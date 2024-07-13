import os
import requests
import pandas as pd
from urllib.parse import urlparse
from wikibaseintegrator.wbi_config import config as wbi_config
from wikibaseintegrator import WikibaseIntegrator, wbi_login
import mwclient
from datetime import datetime
from dateutil.parser import parse as parse_date

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
