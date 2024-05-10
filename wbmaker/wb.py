import os
import configparser
import requests
import pandas as pd
import json
from urllib.parse import urlparse, parse_qs, quote
from wikibaseintegrator.wbi_config import config as wbi_config
from wikibaseintegrator import WikibaseIntegrator, wbi_login
from wikibaseintegrator import models, datatypes
from wikibaseintegrator.wbi_enums import WikibaseDatatype, ActionIfExists, WikibaseDatePrecision, WikibaseSnakType
import mwclient
from datetime import datetime

class WB:
    def __init__(
        self, 
        config_file: str = 'config.ini',
        config_section: str = 'wb',
        cache_props: bool = True):

        if not os.path.exists(config_file):
            raise FileNotFoundError("Configuration file not found.")

        config = configparser.ConfigParser()
        config.read(config_file)

        # WikibaseIntegrator config
        wbi_config['SPARQL_ENDPOINT_URL'] = config[config_section]['sparql_endpoint']
        wbi_config['USER_AGENT'] = config[config_section]['bot_user_agent']
        wbi_config['MEDIAWIKI_API_URL'] = config[config_section]['mediawiki_api_url']
        wbi_config['WIKIBASE_URL'] = config[config_section]['wikibase_url']

        # Establish authentication connection to instance
        if 'bot_user' in config[config_section] and 'bot_pass' in config[config_section]:
            self.login_instance = wbi_login.Login(
                user=config[config_section]['bot_user'],
                password=config[config_section]['bot_pass']
            )
            self.wbi = WikibaseIntegrator(login=self.login_instance, is_bot=True)

            # Establish site for writing to Mediawiki pages
            self.mw_site = mwclient.Site(
                self._get_domain(config[config_section]['wikibase_url']), 
                path='/w/', 
                scheme='https', 
                clients_useragent=config[config_section]['bot_user_agent']
            )
            self.mw_site.login(username=config[config_section]['bot_user'], password=config[config_section]['bot_pass'])

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
        SELECT ?property ?propertyLabel WHERE {
        ?property a wikibase:Property .
        SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
        }
        """

        props = self.sparql_query(q_props)
        props['pid'] = props['property'].str.split('/').str[-1]

        return props.set_index('propertyLabel')['pid'].to_dict()


    def wb_dt(self, dt=datetime.now()):
        return dt.strftime("+%Y-%m-%dT%H:%M:%SZ").split('T')[0] + 'T00:00:00Z'
