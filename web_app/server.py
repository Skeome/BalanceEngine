import json
import csv
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path

app = Flask(__name__, static_folder='.')
CORS(app)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory('.', path)

@app.route('/api/compounds')
def get_compounds():
    catalog_path = Path('../data/compounds/compound-db.csv')
    compounds = []
    if catalog_path.exists():
        with open(catalog_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                compounds.append(row)
    return jsonify(compounds)

if __name__ == '__main__':
    app.run(port=8080, debug=True)
