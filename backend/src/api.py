import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from database.models import db_drop_and_create_all, setup_db, Drink
from auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# db_drop_and_create_all()

# ROUTES
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    }), 200

@app.route('/drinks-detail', methods=['GET'], endpoint='drinks_detail')
@requires_auth('get:drinks-detail')
def drinks_detail():
    try:
        return json.dumps({'success':
        True,
        'drinks': [drink.long() for drink in Drink.query.all()]}), 200
    except:
        return json.dumps({'success': False, 'error': "An error occurred"}), 500

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    req = request.get_json()
    try:
        if isinstance(req_recipe, dict):
            req_recipe = [req_recipe]
        req_recipe = req['recipe']
        drink = Drink()
        drink.recipe = json.dumps(req_recipe)
        drink.title = req['title']
        drink.insert()
    except BaseException:
        abort(400)
    return jsonify({'success': True, 'drinks': [drink.long()]})


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    req = request.get_json()
    if not drink:
        abort(404)
    try:
        req_recipe = req.get('recipe')
        req_title = req.get('title')
        if req_recipe:
            drink.recipe = json.dumps(req['recipe'])
        if req_title:
            drink.title = req_title
        drink.update()
    except BaseException:
        abort(400)
    return jsonify({'success': True, 'drinks': [drink.long()]}), 200


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink:
        abort(404)
    try:
        drink.delete()
    except BaseException:
        abort(400)
    return jsonify({'success': True, 'delete': id}), 200


# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({"error": 422,
        "success": False,
        "message": "Unprocessable"
    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": 404,
        "success": False,
        "message": "Resource not found"
    }), 404

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({"error": error.status_code,
        "success": False,
        "message": error.error['description']
    }), error.status_code


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": 401,
        "success": False,
        "message": 'Unathorized'
    }), 401


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": 500,
        "success": False,
        "message": 'Internal Server Error'
    }), 500


@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": 400,
        "success": False,
        "message": 'Bad Request'
    }), 400


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": 'Method Not Allowed'
    }), 405