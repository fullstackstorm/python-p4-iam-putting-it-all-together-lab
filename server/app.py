#!/usr/bin/env python3

from flask import request, session, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        json = request.get_json()
        password = json.get('password')

        user = User(
            username=json.get('username'),
            image_url=json.get('image_url'),
            bio=json.get('bio'),
        )
        user.password_hash = password

        try:
            db.session.add(user)
            db.session.commit()
            return make_response(user.to_dict(), 201)
        except IntegrityError as e:
            db.session.rollback()
            return make_response({'message': 'Invalid input'}, 422)
        except Exception as e:
            db.session.rollback()
            return make_response({'message': 'An error occurred'}),

class CheckSession(Resource):
    def get(self):
        user_id = session['user_id']
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            return make_response(user.to_dict(), 200)
        
        return make_response({}, 401)

class Login(Resource):
    pass

class Logout(Resource):
    pass

class RecipeIndex(Resource):
    pass

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
