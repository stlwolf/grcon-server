# -*- coding: utf-8 -*-`
# Copyright 2015 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import pycouchdb
import json
from functools import wraps
from flask import Flask, jsonify, request
from watson_developer_cloud import NaturalLanguageClassifierV1

app = Flask(__name__)

DB_HOST = ''


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/nlc', methods=['POST'])
def post_nlc():
    input_text = request.form.get('data')

    # nlcアクセス
    natural_language_classifier = NaturalLanguageClassifierV1(
            username='',
            password='')

    if natural_language_classifier:
        classes = natural_language_classifier.classify('c7fa4ax22-nlc-10554', input_text)

    json_file_path = './restaurants.json'
    with open(json_file_path) as json_file:
        data = json.load(json_file)
        restaurants = data['restaurants']

    for restaurant in restaurants:
        if classes['top_class'] in restaurant['class']:
            restaurant_name = restaurant['name']
            restaurant_url = restaurant['url']
            restaurant_image = restaurant['image']
            restaurant_location = restaurant['location']
            restaurant_budget = restaurant['budget']

    response = {
            'restaurant_name': restaurant_name,
            'restaurant_url': restaurant_url,
            'image_url': restaurant_image,
            'input_text': input_text,
            'location': restaurant_location,
            'budget': restaurant_budget,
        }
    return jsonify(response)

@app.route('/form')
def form():
    return app.send_static_file('form.html')

# couchDB test api
@app.route('/db/put')
def db_insert():
    server = pycouchdb.Server(DB_HOST)
    info = server.info()
    db = server.database("app")
    doc = db.get("3e2c5875dbfe6131b63a4ab1935094df")
    new_doc = db.save({"name": "FOO", "extra": "HOO"})
    list = [
        {'server': info, 'database': db.config()},
        doc,
        new_doc,
    ]

    return jsonify(results=list)

port = os.getenv('PORT', '5000')
if __name__ == "__main__":
        app.run(host='0.0.0.0', port=int(port))
