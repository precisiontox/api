from pathlib import Path
from json import loads
from dotenv import dotenv_values

from flask import Flask, request, jsonify
from flask_cors import CORS
from psql2graphql import generate_endpoints

app = Flask(__name__)
CORS(app)


@app.route('/graphql', methods=['POST', 'OPTIONS'])
def graphql():
    """
    :example: http://127.0.0.1:5000/graphql
    """
    try:
        if request.method == 'OPTIONS':
            return '', 200
        data = schema.execute(loads(request.data)['query'])
        if data.errors:
            return jsonify({"errors": [error.message for error in data.errors]}), 400
        response = jsonify(data.data)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200
    except Exception as e:
        return jsonify({"errors": str(e)}), 500


@app.route('/introspection', methods=['GET'])
def introspection():
    try:
        response = jsonify(tables)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200
    except Exception as e:
        return jsonify({"errors": str(e)}), 500


dotenv_path = Path('.env')
config = dotenv_values(dotenv_path=dotenv_path)
schema, tables = generate_endpoints(config)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
