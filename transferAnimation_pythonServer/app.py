# https://healeycodes.com/javascript/python/beginners/webdev/2019/04/11/talking-between-languages.html
# https://flask.palletsprojects.com/en/1.1.x/quickstart/
# https://flask-cors.corydolphin.com/en/latest/api.html#extension

# FLASK_APP=app.py flask run

# app.py
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS, cross_origin
import json

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'

# cors = CORS(app, resources={r"/hello": {"origins": "http://127.0.0.1:5000/hello"}})
cors = CORS(app, resources={r"/hello/*"})

JSON_DBSummary = None;
JSON_TransferPics = None;
JSON_Timestamp = None;

@app.route('/hello/hi', methods=['GET', 'POST'])
@cross_origin()
def hello():

    # POST request
    if request.method == 'POST':
        print('Incoming..')
        print(request.get_json())  # parse as JSON
        return 'OK', 200

    # GET request
    else:
        # message = {'greeting':'Hello from Flask!'}
        # return jsonify(message)  # serialize and use JSON headers
        with open('./dbSummary.json') as f:
            JSON_DBSummary = json.load(f)
        return jsonify(JSON_DBSummary);


@app.route("/hello/users/")
def list_users():
    # return jsonify(user="joe")
    with open('./transferPics.json') as f:
        JSON_TransferPics = json.load(f)
    return jsonify(JSON_TransferPics);


@app.route("/hello/update/")
def update():
    with open('./test.json') as f:
        JSON_Timestamp = json.load(f)
    return jsonify(JSON_Timestamp);

# @app.route('/foo', methods=['POST'])
# @cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
# def foo():
#     return request.json['inputVar']
#
# @app.route('/test')
# def test_page():
#     # look inside `templates` and serve `index.html`
#     return render_template('index.html')
