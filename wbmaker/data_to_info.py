import requests
from jinja2 import Template
from typing import Dict, List, Optional, Union
from .wb import WB


class DataToInfo:
    """
    A module for filling Wikipedia templates with Wikidata values.
    
    This class provides functionality to:
    - Fetch Wikidata item data by QID
    - Execute SPARQL queries to map Wikidata claims to template parameters
    - Load and fill Wikipedia templates with the mapped data
    """
    
    def __init__(self, wb: Optional[WB] = None):
        """
        Initialize the DataToInfo module.
        
        Args:
            wb: An existing WB instance. If None, a new instance will be created.
        """
        if wb is None:
            self.wb = WB()
        else:
            self.wb = wb
    
    def get_wikidata_item(self, qid: str) -> Optional[Dict]:
        """
        Fetch a Wikidata item by its QID.
        
        Args:
            qid: The Wikidata item ID (e.g., 'Q42')
            
        Returns:
            Dictionary containing the item data, or None if the request fails
        """
        url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException:
            return None
    
    def sparql_to_template_params(
        self, 
        qid: str, 
        sparql_template: str
    ) -> Optional[Dict[str, str]]:
        """
        Execute a SPARQL query with a QID and return template parameters.
        
        The SPARQL query should use the QID as a variable and return key-value
        pairs where keys match template parameter names.
        
        **Important**: The SPARQL query MUST return two variables named 'param' and 'value':
        - 'param': The template parameter name (e.g., 'name', 'birth_date')
        - 'value': The value for that parameter
        
        Args:
            qid: The Wikidata item ID (e.g., 'Q42')
            sparql_template: SPARQL query template that will use the QID.
                           Should contain {qid} placeholder for substitution.
                           Must return ?param and ?value variables.
            
        Returns:
            Dictionary mapping template parameter names to values, or None if query fails
            
        Example:
            sparql_query = '''
            SELECT ?param ?value WHERE {{
              wd:{qid} rdfs:label ?name .
              FILTER(LANG(?name) = "en")
              BIND("name" AS ?param)
              BIND(?name AS ?value)
            }}
            '''
        """
        # Substitute the QID into the SPARQL template
        sparql_query = sparql_template.format(qid=qid)
        
        # Execute the query using the WB instance
        results = self.wb.sparql_query(
            sparql_query, 
            endpoint='https://query.wikidata.org/sparql',
            output='raw'
        )
        
        if not results or 'results' not in results or 'bindings' not in results['results']:
            return None
        
        bindings = results['results']['bindings']
        if not bindings:
            return None
        
        # Convert results to a simple key-value dictionary
        # Requires SPARQL query to return 'param' and 'value' variables
        params = {}
        for binding in bindings:
            # Extract parameter name and value from the binding
            if 'param' in binding and 'value' in binding:
                param_name = binding['param']['value']
                param_value = binding['value']['value']
                params[param_name] = param_value
        
        return params if params else None
    
    def get_wikipedia_template(
        self, 
        template_name: str, 
        lang: str = 'en'
    ) -> Optional[str]:
        """
        Fetch a Wikipedia template by name.
        
        Args:
            template_name: Name of the Wikipedia template (e.g., 'Infobox person')
            lang: Language code for Wikipedia (default: 'en')
            
        Returns:
            Template content as a string, or None if not found
        """
        # Use mwclient to fetch the template
        try:
            # Normalize template name (remove 'Template:' prefix if present)
            if template_name.startswith('Template:'):
                template_name = template_name[9:]
            
            page = self.wb.mw_site.pages[f'Template:{template_name}']
            if page.exists:
                return page.text()
            return None
        except (AttributeError, KeyError):
            return None
    
    def load_template_as_jinja(self, template_content: str) -> Template:
        """
        Load a template string as a Jinja2 template object.
        
        Args:
            template_content: Template content as a string
            
        Returns:
            Jinja2 Template object
        """
        return Template(template_content)
    
    def create_wikitext_template(
        self, 
        template_name: str, 
        params: Dict[str, str]
    ) -> str:
        """
        Create a wikitext template call with parameters.
        
        This generates the standard MediaWiki template syntax:
        {{template_name
        |param1=value1
        |param2=value2
        }}
        
        Args:
            template_name: Name of the template
            params: Dictionary of parameter names to values
            
        Returns:
            Formatted wikitext template call
        """
        lines = [f"{{{{{template_name}"]
        for param, value in params.items():
            lines.append(f"|{param}={value}")
        lines.append("}}")
        return "\n".join(lines)
    
    def fill_template_from_sparql(
        self,
        qid: str,
        template_name: str,
        sparql_template: str
    ) -> Optional[str]:
        """
        Main function to generate a filled Wikipedia template from a QID and SPARQL query.
        
        This is the primary interface that combines all the functionality:
        1. Execute SPARQL query with QID to get template parameters
        2. Generate filled wikitext template
        
        Args:
            qid: Wikidata item ID (e.g., 'Q42')
            template_name: Name of the Wikipedia template
            sparql_template: SPARQL query template with {qid} placeholder
            
        Returns:
            Filled wikitext template, or None if generation fails
        """
        # Get template parameters from SPARQL
        params = self.sparql_to_template_params(qid, sparql_template)
        
        if not params:
            return None
        
        # Create the filled template
        return self.create_wikitext_template(template_name, params)
    
    def fill_template_from_item_data(
        self,
        qid: str,
        template_name: str,
        property_mapping: Dict[str, str]
    ) -> Optional[str]:
        """
        Generate a filled template by directly mapping Wikidata properties to template parameters.
        
        This is an alternative approach that doesn't use SPARQL but directly maps
        properties from a Wikidata item to template parameters.
        
        **Note**: This method only extracts the first value for each property.
        If a property has multiple values (e.g., multiple occupations), only the 
        first one will be included in the template.
        
        Args:
            qid: Wikidata item ID (e.g., 'Q42')
            template_name: Name of the Wikipedia template
            property_mapping: Dictionary mapping template parameter names to Wikidata property IDs
                            e.g., {'name': 'P1559', 'birth_date': 'P569'}
            
        Returns:
            Filled wikitext template, or None if generation fails
        """
        # Fetch the Wikidata item
        item_data = self.get_wikidata_item(qid)
        
        if not item_data or 'entities' not in item_data or qid not in item_data['entities']:
            return None
        
        entity = item_data['entities'][qid]
        claims = entity.get('claims', {})
        
        # Map properties to template parameters
        params = {}
        for param_name, property_id in property_mapping.items():
            if property_id in claims:
                # Get the first claim value (limitation: does not handle multiple values)
                claim = claims[property_id][0]
                if 'mainsnak' in claim and 'datavalue' in claim['mainsnak']:
                    value = claim['mainsnak']['datavalue']['value']
                    # Handle different value types
                    if isinstance(value, str):
                        params[param_name] = value
                    elif isinstance(value, dict):
                        # Handle entity references, time values, etc.
                        if 'id' in value:
                            params[param_name] = value['id']
                        elif 'time' in value:
                            params[param_name] = value['time']
                        elif 'text' in value:
                            params[param_name] = value['text']
                        elif 'amount' in value:
                            params[param_name] = value['amount']
        
        if not params:
            return None
        
        # Create the filled template
        return self.create_wikitext_template(template_name, params)


def get_wikidata_item(qid: str) -> Optional[Dict]:
    """
    Standalone function to fetch a Wikidata item by QID.
    
    This is a convenience function that doesn't require instantiating a 
    DataToInfo or WB class. For integration with other wbmaker functionality,
    use the DataToInfo.get_wikidata_item() method instead.
    
    Args:
        qid: Wikidata item ID (e.g., 'Q42')
        
    Returns:
        Dictionary containing the item data, or None if the request fails
    """
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException:
        return None


def load_template_as_jinja(template_content: str) -> Template:
    """
    Standalone function to load a template string as a Jinja2 template.
    
    Args:
        template_content: Template content as a string
        
    Returns:
        Jinja2 Template object
    """
    return Template(template_content)
