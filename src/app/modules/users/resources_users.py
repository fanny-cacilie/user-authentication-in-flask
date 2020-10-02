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

from app.modules.users.models_users import UserModel
from app.modules.users.schema_users import UserSchema

from security import encrypt_password, check_encrypted_password

USER_NOT_FOUND = "User not found."
USER_CREATED = "User created successfully."
ERROR_SAVING = "An error occurred saving the user."
USER_ALREADY_EXISTS = "An user with name already exists."
USER_DELETED = "User deleted successfully."
INVALID_CREDENTIALS = "Invalid credentials."
USER_LOGGED_OUT = "User <id={}> successfully logged out."


user_schema = UserSchema()
user_list_schema = UserSchema(many=True)


class UserRegister(Resource):
    @classmethod
    def post(cls):
        try:
            user = user_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400

        if UserModel.find_by_username(user.username):
            return {"message": USER_ALREADY_EXISTS}, 400

        try:
            user.password = encrypt_password(user.password)
        except:
            return {"message": "An error occurred while encrypting password."}

        try:
            user.save_to_db()
            return {"message": USER_CREATED}, 201
        except:
            return {"message": ERROR_SAVING}, 500


class User(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if user:
            return user_schema.dump(user), 200
        return {"message": USER_NOT_FOUND}, 404

    @classmethod
    def put(cls, user_id):
        user_json = request.get_json()
        user = UserModel.find_by_id(user_id)

        if user:
            user.username = user_json["username"]
        else:
            return {"message": "An error occurre while updatig user."}, 500

        user.save_to_db()

        return user_schema.dump(user), 200

    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if user:
            user.delete_from_db()
            return {"message": USER_DELETED}, 200
        return {"message": USER_NOT_FOUND}, 404


class UserList(Resource):
    @classmethod
    def get(cls):
        users = user_list_schema.dump(UserModel.find_all())
        return {"users": users}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        """
        Gets data from parser to find user in database and checks password.
        Checks and returns access token.
        """
        try:
            user_json = request.get_json()
            user_data = user_schema.load(user_json)
        except ValidationError as err:
            return err.messages, 400

        user = UserModel.find_by_username(user_data.username)

        if not user:
            return {"message": USER_NOT_FOUND.format(user_data["username"])}

        if check_encrypted_password(user_data.password, user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            return {"access_token": access_token}, 200

        return {"message": INVALID_CREDENTIALS}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        jwt_id = get_raw_jwt()["jti"]
        user_id = get_jwt_identity()
        BLACKLIST.add(jwt_id)
        return {"message": USER_LOGGED_OUT.format(user_id)}, 200
