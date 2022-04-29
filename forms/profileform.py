from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class ProfileForm(FlaskForm):
    add_image = SubmitField('Изменить изображение')
    quit_button = SubmitField('Выйти')
    main_page_button = SubmitField('Моя страница')
    feed_button = SubmitField('Лента')
    message_button = SubmitField('Сообщения')
    friends_button = SubmitField('Друзья')
    publics_button = SubmitField('Сообщества')
    edit_button = SubmitField('Редактировать профиль')
    add_friends = SubmitField('Добавить в друзья')
    remove_friends = SubmitField("Удалить из друзей")
    cancel_request = SubmitField("Отменить заявку")
    write_message = SubmitField('Написать сообщение')
    accept_rq = SubmitField("Принять запрос")
    decline_rq = SubmitField('Отклонить запрос')
    send_post = SubmitField("Опубликовать запись")
    post_text = SubmitField('Текст записи')
