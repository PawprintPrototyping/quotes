### This is a flask app which serves quotes. It has a single endpoint /quotes which returns a random quote from a list of quotes.
import random
import json
import flask
from datetime import datetime

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

def load_quotes():
    with open('quotes.json') as f:
        return json.load(f)

def save_quotes(quotes_data):
    with open('quotes.json', 'w') as f:
        json.dump(quotes_data, f, indent=2, ensure_ascii=False)

quotes = load_quotes()
        
@app.route('/', methods=['GET', 'POST'])
def home():
    if flask.request.method == 'POST':
        # Get form data
        new_quote = {
            'what': flask.request.form['what'],
            'when': flask.request.form['when'].replace('T', 'T') + ':00-08:00',  # Convert to ISO8601 with timezone
            'who': flask.request.form['who'],
            'where': flask.request.form['where'],
            'why': flask.request.form['why']
        }

        # Load current quotes
        quotes_data = load_quotes()

        # Add new quote
        quotes_data['quotes'].append(new_quote)

        # Save updated quotes
        save_quotes(quotes_data)

        # Reload quotes in memory
        global quotes
        quotes = quotes_data

        # Redirect to home to prevent form resubmission
        return flask.redirect('/')

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
    app.run(port=5000, debug=True)
