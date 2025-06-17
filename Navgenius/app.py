from flask import Flask, render_template, jsonify
import os
import json
from route_generator import main_model_function  # Your route-generating function

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run-model')
def run_model():
    try:
        main_model_function()  # This should generate `fulldf.json`, `destdf.json`, `srcdf.json`
        return jsonify({'status': 'Model run successfully!'})
    except Exception as e:
        return jsonify({'status': f'Error: {str(e)}'}), 500

@app.route('/get-data')
def get_data():
    try:
        with open('fulldf.json') as f:
            fulldf = json.load(f)
        with open('destdf.json') as f:
            destdf = json.load(f)
        with open('srcdf.json') as f:
            srcdf = json.load(f)
        return jsonify({
            'fulldf': fulldf,
            'destdf': destdf,
            'srcdf': srcdf
        })
    except Exception as e:
        return jsonify({'status': f'Error loading data: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
