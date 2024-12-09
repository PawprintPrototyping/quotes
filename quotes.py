### This is a flask app which serves quotes. It has a single endpoint /quotes which returns a random quote from a list of quotes.
import random
import json
import flask
from urllib.parse import urlparse

def is_uri(string):
    if string.startswith('https://'):
        return True
    else:
        return False

def linkify(string, href=None):
    if href is None:
        href = string
    return f'<a href="{href}" target="_blank">{string}</a>'

app = flask.Flask(__name__)
with open('quotes.json') as f:
    quotes = json.load(f)
        
@app.route('/', methods=['GET'])
def home():
    quote = get_quote()
    if is_uri(quote['where']):
        quote['what'] = linkify(quote['what'], quote['where'])

    for thing in ['who', 'why']:
        if is_uri(quote[thing]):
            quote[thing] = linkify(quote[thing])

    return flask.render_template('home.html', quote=quote)

@app.route('/quotes', methods=['GET'])
def get_quote():
    return random.choice(quotes['quotes'])

@app.route('/quotes/<int:index>', methods=['GET'])
def get_quote_by_index(index):
    return quotes['quotes'][index]

if __name__ == '__main__':
    app.run(debug=True)