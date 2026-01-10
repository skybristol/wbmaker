# WBMaker
This alpha package helps establish an authenticated connection with a Wikibase instance and provides a number of functions for building items using the wikibaseintegrator package and working with Wikimedia pages (e.g., "item talk" pages) using the mwclient package. While it is simple enough to work with these packages separately, it is helpful to provide a lightweight layer of abstraction for many of the tasks needed in developing bot-based applications and data processing pipelines.

I am planning on building in additional functionality that I find most commonly used when developing bots that take action on Wikidata or another Wikibase instance.

## Installation

```pip install wbmaker```

or install from source

```git clone https://github.com/skybristol/wbmaker```

## Environment Variables
The WB class operates on a set of environment variables that set up and authorize interactions with a Wikibase instance, including Wikidata. These variables are required by one or both of the underlying packages, [wikibaseintegrator](https://github.com/LeMyst/WikibaseIntegrator) and [mwclient](https://github.com/mwclient/mwclient) used in wbmaker. Instantiating the class will prompt for the following basic variables and set them if not supplied in the operating environment.

* WB_URL: base URL for the Wikibase instance (e.g., https://www.wikidata.org/)
* WB_SPARQL_ENDPOINT: SPARQL endpoint for the Wikibase instance (e.g., https://query.wikidata.org/sparql)
* MEDIAWIKI_API: Mediawiki API URL for the Wikibase instance (e.g., https://www.wikidata.org/w/api.php)
* WB_BOT_USER_AGENT: the user agent string to use in actions; link to code and/or contact information encouraged (e.g., "MyBot/1.0")

If you will be making edits, the following are also required. If these are not provided, the login section of the class will not be invoked, and you will be limited to read-only operations.

* WB_BOT_USER: bot user name authorized to operate on the Wikibase instance
* WB_BOT_PASS: bot user's password

## Modules

### data_to_info

The `data_to_info` module provides functionality for filling Wikipedia templates with Wikidata values. This enables automated generation of Wikipedia infoboxes and other templates using data from Wikidata.

#### Quick Example

```python
from wbmaker.data_to_info import DataToInfo

# Initialize the module
data_to_info = DataToInfo()

# Approach 1: Direct property mapping
property_mapping = {
    'birth_date': 'P569',  # date of birth
    'occupation': 'P106'    # occupation
}

filled_template = data_to_info.fill_template_from_item_data(
    qid='Q42',  # Douglas Adams
    template_name='Infobox person',
    property_mapping=property_mapping
)

# Approach 2: SPARQL-based (more flexible)
sparql_query = """
SELECT ?param ?value WHERE {{
  wd:{qid} rdfs:label ?name .
  FILTER(LANG(?name) = "en")
  BIND("name" AS ?param)
  BIND(?name AS ?value)
}}
"""

filled_template = data_to_info.fill_template_from_sparql(
    qid='Q42',
    template_name='Infobox person',
    sparql_template=sparql_query
)
```

#### Key Features

* **Two approaches**: SPARQL-based for complex queries, or direct property mapping for simple use cases
* **Modular design**: Individual functions can be invoked separately
* **Jinja2 support**: Load templates as Jinja2 objects for advanced templating
* **Wikipedia integration**: Fetch Wikipedia templates directly via mwclient
* **Wikidata integration**: Retrieve item data and execute SPARQL queries

#### Available Functions

* `get_wikidata_item(qid)` - Fetch a Wikidata item by QID
* `sparql_to_template_params(qid, sparql_template)` - Execute SPARQL query to get template parameters
* `get_wikipedia_template(template_name)` - Fetch a Wikipedia template by name
* `load_template_as_jinja(content)` - Load template content as Jinja2 template
* `create_wikitext_template(name, params)` - Generate wikitext template syntax
* `fill_template_from_sparql(qid, template_name, sparql_template)` - Main SPARQL-based approach
* `fill_template_from_item_data(qid, template_name, property_mapping)` - Main direct mapping approach