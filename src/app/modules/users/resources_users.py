from flask import request
from flask_restful import Resource
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_raw_jwt,
)
from marshmallow import ValidationError
from blacklist import BLACKLIST
from security import encrypt_password, check_encrypted_password

from libs.strings import gettext

from app.modules.users.models_users import UserModel
from app.modules.users.schema_users import UserSchema


user_schema = UserSchema()
user_list_schema = UserSchema(many=True)


class UserRegister(Resource):
    @classmethod
    def post(cls):

        try:
            user = user_schema.load(request.get_json())

            if UserModel.find_by_username(user.username):
                return {"message": gettext("user_username_exists")}, 400

            user.password = encrypt_password(user.password)
            user.save_to_db()
            return {"message": gettext("user_registered")}, 201

        except:
            return {"message": gettext("user_error_creating")}, 500


class User(Resource):
    @classmethod
    @jwt_required
    def get(cls, user_id):

        try:
            user = UserModel.find_by_id(user_id)
            if user:
                return user_schema.dump(user), 200
            return {"message": gettext("user_not_found")}, 404
        except:
            return {"message": gettext("user_error_reading.")}, 500

    @classmethod
    @jwt_required
    def put(cls, user_id):

        try:
            user_json = request.get_json()
            user = UserModel.find_by_id(user_id)

            if user:
                user.name = user_json["name"]
            else:
                return {"message": gettext("user_not_found")}, 404

            user.save_to_db()

            return user_schema.dump(user), 200

        except:
            return {"message": gettext("user_error_updating.")}, 500

    @classmethod
    @jwt_required
    def delete(cls, user_id):
        try:
            user = UserModel.find_by_id(user_id)
            if user:
                user.delete_from_db()
                return {"message": gettext("user_deleted")}, 200
            return {"message": gettext("user_not_found")}, 404
        except:
            return {"message": gettext("user_error_deleting")}, 500


class UserList(Resource):
    @classmethod
    @jwt_required
    def get(cls):
        try:
            users = user_list_schema.dump(UserModel.find_all())
            return {"users": users}, 200
        except:
            return {"message": gettext("user_not_found")}


class UserLogin(Resource):
    @classmethod
    def post(cls):
        """
        Gets data from parser to find user in database and checks password.
        Checks and returns access token.
        """
        try:
            user_json = request.get_json()
            user_data = user_schema.load(
                user_json, partial=("name", "company_name", "email")
            )

            user = UserModel.find_by_username(user_data.username)

            if not user:
                return {"message": gettext("user_not_found")}, 404

            if check_encrypted_password(user_data.password, user.password):
                access_token = create_access_token(identity=user.id, fresh=True)
                return {"access_token": access_token}, 200

            return {"message": gettext("user_invalid_credentials")}, 401

        except:
            return {"message": gettext("user_error_logging_in")}, 500


class UserLogout(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        try:
            jwt_id = get_raw_jwt()["jti"]
            user_id = get_jwt_identity()
            BLACKLIST.add(jwt_id)
            return {"message": gettext("user_logged_out")}, 200
        except:
            return {"message": gettext("user_error_logging_out")}, 500
