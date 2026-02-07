# WBMaker

[![PyPI version](https://badge.fury.io/py/wbmaker.svg)](https://badge.fury.io/py/wbmaker)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This alpha package helps establish an authenticated connection with a Wikibase instance and provides functions for building items using the wikibaseintegrator package and working with Wikimedia pages (e.g., "item talk" pages) using the mwclient package. While it is simple enough to work with these packages separately, wbmaker provides a lightweight layer of abstraction for many of the tasks needed in developing bot-based applications and data processing pipelines.

## Features

- 🔐 Easy authentication with Wikibase instances (including Wikidata)
- 🔧 Simplified item creation and editing
- 📝 MediaWiki page management (talk pages, etc.)
- 🔍 SPARQL query execution with result formatting
- 🧩 Property mapping and caching
- 🌐 Path analysis for Wikidata classification

## Installation

```bash
pip install wbmaker
```

Or install from source:

```bash
git clone https://github.com/skybristol/wbmaker
cd wbmaker
poetry install
```

## Environment Variables

The WB class operates on a set of environment variables that set up and authorize interactions with a Wikibase instance, including Wikidata. These variables are required by one or both of the underlying packages, [wikibaseintegrator](https://github.com/LeMyst/WikibaseIntegrator) and [mwclient](https://github.com/mwclient/mwclient) used in wbmaker. Instantiating the class will prompt for the following basic variables and set them if not supplied in the operating environment.

### Required Variables

* `WB_URL`: base URL for the Wikibase instance (e.g., https://www.wikidata.org/)
* `WB_SPARQL_ENDPOINT`: SPARQL endpoint for the Wikibase instance (e.g., https://query.wikidata.org/sparql)
* `MEDIAWIKI_API`: Mediawiki API URL for the Wikibase instance (e.g., https://www.wikidata.org/w/api.php)
* `WB_BOT_USER_AGENT`: the user agent string to use in actions; link to code and/or contact information encouraged (e.g., "MyBot/1.0")

### Optional Variables (for editing)

If you will be making edits, the following are also required. If these are not provided, the login section of the class will not be invoked, and you will be limited to read-only operations.

* `WB_BOT_USER`: bot user name authorized to operate on the Wikibase instance
* `WB_BOT_PASS`: bot user's password

### Using .env file

You can create a `.env` file in your project root:

```env
WB_URL=https://www.wikidata.org/
WB_SPARQL_ENDPOINT=https://query.wikidata.org/sparql
MEDIAWIKI_API=https://www.wikidata.org/w/api.php
WB_BOT_USER_AGENT=MyBot/1.0 (https://github.com/myusername/mybot)
WB_BOT_USER=MyBotUsername
WB_BOT_PASS=MyBotPassword
```

## Basic Usage

```python
from wbmaker import WB, Item

# Initialize connection (read-only if no credentials provided)
wb = WB()

# Run a SPARQL query
query = """
SELECT ?item ?itemLabel WHERE {
  ?item wdt:P31 wd:Q5.  # instances of human
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 10
"""
results = wb.sparql_query(query, output='dataframe')
print(results)

# Create or update an item
item_data = {
    'qid': 'Q123456',  # Leave empty for new items
    'label': 'Example Item',
    'description': 'An example item for demonstration',
    'aliases': ['Demo Item', 'Test Item'],
    'claims': [
        {
            'property_name': 'instance of',
            'value': 'Q5',  # human
        }
    ]
}

item = Item(item_data, wb=wb, commit=True, summary='Created example item')
```

## Development Status

This package is in alpha status. Additional functionality is planned based on common patterns in Wikidata/Wikibase bot development.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- [GitHub Repository](https://github.com/skybristol/wbmaker)
- [PyPI Package](https://pypi.org/project/wbmaker/)
- [Issue Tracker](https://github.com/skybristol/wbmaker/issues)
