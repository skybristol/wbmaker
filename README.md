# WBMaker
This alpha package helps establish an authenticated connection with a Wikibase instance and provides a number of functions for building items using the wikibaseintegrator package and working with Wikimedia pages (e.g., "item talk" pages) using the mwclient package. While it is simple enough to work with these packages separately, it is helpful to provide a lightweight layer of abstraction for many of the tasks needed in developing bot-based applications and data processing pipelines.

I am planning on building in additional functionality that I find most commonly used when developing bots that take action on Wikidata or another Wikibase instance.

## Installation

```pip install wbmaker```

or install from source

```git clone https://github.com/skybristol/wbmaker```

## Config.ini
The package assumes availability of a config.ini defaulting to the current directory and containing a default [wb] object with configuration details. These can include a bot user and password for authenticated connections. Parameters can be set when calling the WB() class.