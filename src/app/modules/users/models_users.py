from db import db


class UserModel(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    company_name = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(40), nullable=False)
    username = db.Column(db.String(40), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username: str):
        return UserModel.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id: str):
        return UserModel.query.filter_by(id=_id).first()

    @classmethod
    def find_all(cls):
        return UserModel.query.all()
