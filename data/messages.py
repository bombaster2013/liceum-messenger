import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Message(SqlAlchemyBase):
    __tablename__ = 'messages'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    by = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    to = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, default=datetime.datetime.now)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=False)
