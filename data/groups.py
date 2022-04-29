import datetime

import sqlalchemy
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class Group(SqlAlchemyBase):
    __tablename__ = 'groups'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.String, default='0.jpg')
    author = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    subscriptions = sqlalchemy.Column(sqlalchemy.String, nullable=True)