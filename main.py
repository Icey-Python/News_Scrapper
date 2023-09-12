from flask import Flask, jsonify
import json

app = Flask(__name__)

# Load categories from the JSON file
with open('content.json', 'r') as json_file:
    categories_data = json.load(json_file)

# Define a route to get the categories in JSON format
@app.route('/categories', methods=['GET'])
def get_categories():
    return jsonify(categories_data)

if __name__ == '__main__':
    app.run(debug=True)
