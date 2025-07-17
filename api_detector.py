# File: api_detector.py

import requests
from bs4 import BeautifulSoup
import json
import re
from flask import Flask, request, jsonify

# --- This is our Shopify detection function ---
def find_shopify_theme(url):
    try:
        # Use a common user-agent to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Set a timeout to prevent the request from hanging forever
        response = requests.get(url, headers=headers, timeout=10)
        # This will raise an error if the request was not successful (e.g., 404 Not Found)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return "Error: Could not fetch the URL. Please check if it's correct and publicly accessible."

    soup = BeautifulSoup(response.text, 'html.parser')
    script_tag = soup.find('script', string=re.compile('Shopify.theme'))

    if script_tag:
        script_content = script_tag.string
        match = re.search(r'Shopify.theme = ({.*?});', script_content)
        if match:
            theme_json = match.group(1)
            try:
                theme_data = json.loads(theme_json)
                theme_name = theme_data.get('name', 'Theme name not found in script')
                return f"The theme is: {theme_name}"
            except json.JSONDecodeError:
                return "Error: Could not decode theme data."
    return "Could not find a Shopify theme. The store might be using a custom or heavily modified theme."


# --- This is the API server part using Flask ---
app = Flask(__name__)

# This is the main function that will run when a request comes in
@app.route('/detect', methods=['GET'])
def detect_theme_api():
    # Get the URL from a query parameter (e.g., /detect?url=https://example.com)
    store_url = request.args.get('url')

    if not store_url:
        return jsonify({'error': 'No URL provided. Please add ?url=... to the request.'}), 400

    # Run our function and get the result
    result_message = find_shopify_theme(store_url)

    # Return the result in a clean JSON format
    return jsonify({'result': result_message})
