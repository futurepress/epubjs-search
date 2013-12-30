from flask import Flask
from flask import request
from flask import jsonify
from flask import g

from epubsearch import EpubIndexer
from epubsearch import crossdomain

app = Flask(__name__)
index = EpubIndexer("whoosh")

@app.route("/")
def home():
    return "try /search?q=whale"

@app.route("/search", methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def search():
    query = request.args.get('q')
    results = index.search(query)
    return jsonify(**results)

@app.after_request
def after_request(response):
    if getattr(g, 'cors', False):
        response.headers['Access-Control-Allow-Origin'] = "*"
        response.headers['Access-Control-Allow-Headers'] = 'Accept, Content-Type, Origin, X-Requested-With'

    return response
    
if __name__ == "__main__":
    app.run(debug=True)

