epubjs-search - Full Text Indexing and Retrieval for Epub Files
=============

Engines Supported
---------------------

* Whoosh
* Cheshire3

How To Use (assumes a Python 2.7 environment with pip and virtualenv) 
---------------------

Clone the Repository

`$ git clone https://github.com/futurepress/epubjs-search.git`
`$ cd epubjs-search`

Load a virtual environment for Python

`$ virtualenv venv`
`$ source venv/bin/activate`
`$ pip install -r requirements.txt`

Add an unzipped epub to the source directory, say /your_epub/ then run

`$ python indexer.py --i your_epub`

Finally run the search api

`$ python search.py`

Flask should run on localhost:5000/ and you can query the server with the /search route and the parameter q, like:

localhost:5000/search?q=test
