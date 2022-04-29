from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class FriendsForm(FlaskForm):
    quit_button = SubmitField('Выйти')
    main_page_button = SubmitField('Моя страница')
    feed_button = SubmitField('Лента')
    message_button = SubmitField('Сообщения')
    friends_button = SubmitField('Друзья')
    publics_button = SubmitField('Сообщества')
    requests_button = SubmitField('Запросы в друзья')