from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired


class GroupViewForm(FlaskForm):
    quit_button = SubmitField('Выйти')
    main_page_button = SubmitField('Моя страница')
    feed_button = SubmitField('Лента')
    message_button = SubmitField('Сообщения')
    friends_button = SubmitField('Друзья')
    publics_button = SubmitField('Сообщества')
    send_post = SubmitField('Опубликовать запись')
    subscribe_button = SubmitField('Подписаться')
    unsubscribe_button = SubmitField('Отписаться')
