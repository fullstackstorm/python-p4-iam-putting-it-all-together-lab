#!/usr/bin/env python3

from flask import request, session, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

# @app.before_request
# def check_if_logged_in():
#     if not session.get('user_id') and request.endpoint == 'recipes' :
#         return make_response({'error': 'Unauthorized'}, 401)

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
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.authenticate(password):
            session['user_id'] = user.id
            return make_response(user.to_dict(), 200)
        
        return make_response({}, 401)
    
class Logout(Resource):
    def delete(self):
        if session['user_id']:
            session['user_id'] = None
            return make_response({}, 204)
        else:
            return make_response({}, 401)

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            # If the user is logged in, retrieve and return their recipes
            recipes = Recipe.query.filter(Recipe.user_id == user_id).all()
            recipes_data = [recipe.to_dict() for recipe in recipes]
            return make_response(recipes_data, 200)
        else:
            # If the user is not logged in, return an unauthorized error
            return make_response({'error': 'Unauthorized'}, 401)

    def post(self):
        user_id = session.get('user_id')
        if user_id:
            # If the user is logged in, try to create a new recipe
            json = request.get_json()
            title = json.get('title')
            instructions = json.get('instructions')
            minutes_to_complete = json.get('minutes_to_complete')
            
            if not title or not instructions or not minutes_to_complete:
                # Check if required data is missing
                return make_response({'message': 'Title, instructions, and minutes_to_complete are required'}, 422)
            
            # Create a new recipe and associate it with the logged-in user
            recipe = Recipe(
                title=title,
                instructions=instructions,
                minutes_to_complete=minutes_to_complete,
                user_id=user_id
            )
            
            try:
                db.session.add(recipe)
                db.session.commit()
                return make_response(recipe.to_dict(), 201)
            except IntegrityError as e:
                db.session.rollback()
                return make_response({'message': 'Invalid input'}, 422)
            except Exception as e:
                db.session.rollback()
                return make_response({'message': 'An error occurred'}, 500)
        else:
            # If the user is not logged in, return an unauthorized error
            return make_response({'error': 'Unauthorized'}, 401)


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
