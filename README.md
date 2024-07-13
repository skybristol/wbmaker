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

If you will be making edits, the following are also required. If these are not provided, the login section of the class will not be invoked, and you will be limited to read-only operations.

* WB_BOT_USER: bot user name authorized to operate on the Wikibase instance
* WB_BOT_PASS: bot user's password