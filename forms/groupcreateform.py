from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired


class GroupCreateForm(FlaskForm):
    quit_button = SubmitField('Выйти')
    main_page_button = SubmitField('Моя страница')
    feed_button = SubmitField('Лента')
    message_button = SubmitField('Сообщения')
    friends_button = SubmitField('Друзья')
    publics_button = SubmitField('Сообщества')
    requests_button = SubmitField('Запросы в друзья')
    group_name = StringField('Название группы')
    group_description = StringField("Краткое описание")
    create_group = SubmitField('Создать группу')
    group_avatar = FileField('Добавить изображение')