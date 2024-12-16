### Test harness for this project.
import json
import datetime
import pytest
from quotes import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_quotes():
    with open('quotes.json', encoding='utf8') as f:
        quotes = json.load(f)
    assert 'quotes' in quotes
    assert isinstance(quotes['quotes'], list)
    assert len(quotes['quotes']) > 0
    for quote in quotes['quotes']:
        for mandatory_keys in ['what', 'who', 'why', 'where', 'when']:
            assert mandatory_keys in quote
            assert '<' not in quote[mandatory_keys] and '>' not in quote[mandatory_keys], f'Potential XSS in quote: {quote}'
            assert isinstance(quote[mandatory_keys], str)
            assert quote[mandatory_keys]
            try:
                datetime.datetime.fromisoformat(quote['when'])
            except ValueError:
                assert False, f'Invalid datetime in quote: {quote}'

def test_post_quote(client):
    # Save initial quotes
    with open('quotes.json', encoding='utf8') as f:
        initial_quotes = json.load(f)
    initial_count = len(initial_quotes['quotes'])
    
    # Test data
    test_quote = {
        'what': 'Test quote content',
        'when': '2023-12-25T12:00',  # Will be converted to ISO8601
        'who': 'Test Author',
        'where': 'https://example.com',
        'why': 'For testing purposes'
    }
    
    # Submit form
    response = client.post('/', data=test_quote)
    assert response.status_code == 302  # Should redirect
    
    # Verify quote was added
    with open('quotes.json', encoding='utf8') as f:
        updated_quotes = json.load(f)
    assert len(updated_quotes['quotes']) == initial_count + 1

    # Get the newly added quote
    new_quote = updated_quotes['quotes'][-1]

    # Verify all fields
    assert new_quote['what'] == test_quote['what']
    assert new_quote['who'] == test_quote['who']
    assert new_quote['where'] == test_quote['where']
    assert new_quote['why'] == test_quote['why']

    # Verify datetime was properly converted to ISO8601
    assert new_quote['when'] == test_quote['when'] + ':00-08:00'

    # Verify it can be parsed as ISO8601
    datetime.datetime.fromisoformat(new_quote['when'])

    # Restore original quotes
    with open('quotes.json', 'w', encoding='utf8') as f:
        json.dump(initial_quotes, f, indent=2, ensure_ascii=False)

def test_post_quote_required_fields(client):
    # Test missing required field
    incomplete_quote = {
        'what': 'Test quote content',
        'when': '2023-12-25T12:00',
        'who': 'Test Author',
        'where': 'https://example.com'
        # Missing 'why' field
    }
    
    response = client.post('/', data=incomplete_quote)
    assert response.status_code == 400  # Should fail with Bad Request
