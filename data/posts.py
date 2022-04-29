import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Post(SqlAlchemyBase):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.Date,
                                     default=datetime.date.today())
    public_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')