import os

import flask
from flask import render_template, request, make_response, url_for

from data import db_session
from data.groups import Group
from data.messages import Message
from data.posts import Post
from data.users import User
from forms.editform import EditForm
from forms.friendsform import FriendsForm
from forms.groupcreateform import GroupCreateForm
from forms.groupsform import GroupsForm
from forms.groupviewform import GroupViewForm
from forms.loginform import LoginForm
from forms.mainform import MainForm
from forms.messageform import MessageForm
from forms.messagesform import MessagesForm
from forms.profileform import ProfileForm
from forms.regform import RegForm
from forms.requestform import RequestForm

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
UPLOAD_FOLDER = 'static/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


class PostForFeed:
    def __init__(self, name, surname, img, content):
        self.name = name
        self.surname = surname
        self.img = img
        self.content = content


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def start():
    return flask.redirect("/login")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    res = make_response(render_template('author.html', form=form, username="1", password="1", title='Авторизация'))
    user_id = request.cookies.get('user_id')
    if user_id is not None:
        return flask.redirect('/feed')
    if request.method == 'POST':
        if form.submit.data:
            if "" in [form.username.data, form.password.data]:
                return render_template('author.html', form=form, username=form.username.data,
                                       password=form.password.data, title='Авторизация')
            db_sess = db_session.create_session()
            users = db_sess.query(User).filter(User.login == form.username.data)
            if list(users) != [] and users[0].check_password(form.password.data):
                res.set_cookie('user_id', str(users[0].id))
                res.headers['location'] = url_for('feed')
                return res, 302
            return render_template('author.html', form=form, login='1', password='1', title='Авторизация', err='1')
        else:
            return flask.redirect('/registration')
    elif request.method == 'GET':
        return render_template('author.html', form=form, login='1', password='1', title='Авторизация')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegForm()
    res = make_response(
        render_template('reg.html', form=form, name="1", surname="1", login="1", password="1", title="Регистрация"))
    if request.method == 'POST':
        name = form.name.data
        surname = form.surname.data
        lgn = form.login.data
        pword = form.password.data
        if "" in [name, surname, login, pword]:
            return render_template('reg.html', form=form, name=name, password=pword, surname=surname, login=lgn,
                                   title='Регистрация')
        try:
            filename = form.add_image.data.filename
            if filename and allowed_file(filename):
                filename = str(len([f for f in os.listdir(os.path.join(app.config['UPLOAD_FOLDER']))])) + \
                           os.path.splitext(filename)[1]
                form.add_image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if filename == '':
                filename = None
            user = User()
            user.name = name
            user.surname = surname
            user.login = lgn
            user.set_password(pword)
            if filename is not None:
                user.image = filename
            db_sess = db_session.create_session()
            db_sess.add(user)
            db_sess.commit()
            res.set_cookie('user_id', str(user.id))
            res.headers['location'] = url_for('feed')
            return res, 302
        except Exception as e:
            return render_template('reg.html', form=form, name=name, password=pword, surname=surname, login=lgn,
                                   title='Регистрация', err='Логин уже занят')
    elif request.method == 'GET':
        return res


@app.route('/feed', methods=['GET', 'POST'])
def feed():
    form = MainForm()
    user_id = request.cookies.get('user_id')
    if user_id is None:
        return flask.redirect('/login')
    db_sess = db_session.create_session()
    usr = db_sess.query(User).filter(User.id == user_id).first()
    groups = db_sess.query(Group)
    subscriptions = []
    for group in groups:
        if group.subscriptions is not None:
            tmp = group.subscriptions.split()
        else:
            continue
        if user_id in tmp:
            subscriptions.append(str(group.id))
    if usr.friends is not None:
        friends = usr.friends.split()
    else:
        friends = []
    psts = []
    posts = db_sess.query(Post)
    tmp = []
    for post in posts:
        if str(post.public_id) in subscriptions or str(post.user_id) in friends:
            tmp.append(post)
    posts = tmp
    print(posts)
    for post in posts:
        if post.public_id is not None:
            group = db_sess.query(Group).filter(Group.id == post.public_id).first()
            name = group.name
            surname = ''
            img = group.image
            content = post.content
            tmp = PostForFeed(name, surname, img, content)
        else:
            user = db_sess.query(User).filter(User.id == post.user_id).first()
            name = user.name
            surname = user.surname
            img = user.image
            content = post.content
            tmp = PostForFeed(name, surname, img, content)
        psts.append(tmp)
    res = make_response(
        render_template('main.html', form=form, title='Лента', top_name=usr.name, top_surname=usr.surname,
                        posts=psts))
    if request.method == 'POST':
        if form.quit_button.data:
            res.set_cookie('user_id', request.cookies.get('user_id'), max_age=0)
            res.headers['location'] = url_for('login')
            return res, 302
        elif form.friends_button.data:
            return flask.redirect('/friends')
        elif form.publics_button.data:
            return flask.redirect('/groups')
        elif form.feed_button.data:
            return flask.redirect('/feed')
        elif form.main_page_button.data:
            return flask.redirect(f'/profile/{user_id}')
        elif form.message_button.data:
            return flask.redirect('/messages')
    elif request.method == 'GET':
        return res


@app.route('/friends', methods=['GET', 'POST'])
def friends():
    form = FriendsForm()
    user_id = request.cookies.get('user_id')
    if user_id is None:
        return flask.redirect('/login')
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id)[0]
    if user.friends:
        friends_lst = [int(i) for i in user.friends.split()]
    else:
        friends_lst = []
    db_sess = db_session.create_session()
    frs = db_sess.query(User).filter(User.id.in_(friends_lst))
    res = make_response(
        render_template('friends.html', form=form, title='Друзья', top_name=user.name, top_surname=user.surname,
                        users=frs))
    if request.method == 'POST':
        if form.quit_button.data:
            res.set_cookie('user_id', request.cookies.get('user_id'), max_age=0)
            res.headers['location'] = url_for('login')
            return res, 302
        elif form.friends_button.data:
            return flask.redirect('/friends')
        elif form.publics_button.data:
            return flask.redirect('/groups')
        elif form.feed_button.data:
            return flask.redirect('/feed')
        elif form.requests_button.data:
            return flask.redirect('/requests')
        elif form.main_page_button.data:
            return flask.redirect(f'/profile/{user_id}')
        elif form.message_button.data:
            return flask.redirect('/messages')
        for key in request.form:
            if key.startswith('remove_button.'):
                uid = key.split('.')[-1]
                db_sess = db_session.create_session()
                user = db_sess.query(User).filter(User.id == user_id).first()
                if user.friends:
                    frs_lst = user.friends.split()
                else:
                    frs_lst = []
                print(frs_lst)
                print(uid)
                frs_lst.remove(uid)
                if frs_lst:
                    user.friends = ' '.join(frs_lst)
                else:
                    user.friends = None
                db_sess.commit()
                return flask.redirect('/friends')
            elif key.startswith('open_profile.'):
                uid = key.split('.')[-1]
                return flask.redirect(f'/profile/{uid}')
            elif key.startswith('write_message.'):
                uid = key.split('.')[-1]
                return flask.redirect(f"/message/{uid}")
    elif request.method == 'GET':
        return res


@app.route('/requests', methods=['GET', 'POST'])
def requests():
    form = RequestForm()
    user_id = request.cookies.get('user_id')
    if user_id is None:
        return flask.redirect('/login')
    db_sess = db_session.create_session()
    users = db_sess.query(User).filter(User.id != user_id)
    main_user = db_sess.query(User).filter(User.id == user_id).first()
    tp_name = main_user.name
    tp_surname = main_user.surname
    tmp = []
    for user in users:
        if user.requests is not None:
            user_rq = user.requests.split()
        else:
            user_rq = []
        if user_id in user_rq:
            tmp.append(user)
    users = tmp
    res = make_response(
        render_template('requests.html', users=users, form=form, top_name=tp_name, top_surname=tp_surname))
    if request.method == 'POST':
        for key in request.form:
            if key.startswith('accept_button.'):
                uid = key.split('.')[-1]
                db_sess = db_session.create_session()
                user = db_sess.query(User).filter(User.id == uid).first()
                rq_lst = user.requests.split()
                rq_lst.remove(user_id)
                if user.friends is not None:
                    fr_lst = user.friends.split()
                else:
                    fr_lst = []
                fr_lst.append(user_id)
                user.friends = ' '.join(fr_lst)
                user.requests = ' '.join(rq_lst) if rq_lst else None
                db_sess.commit()
                return flask.redirect('/requests')
            if key.startswith('decline_button.'):
                uid = key.split('.')[-1]
                db_sess = db_session.create_session()
                user = db_sess.query(User).filter(User.id == uid).first()
                rq_lst = user.requests.split()
                rq_lst.remove(user_id)
                user.requests = ' '.join(rq_lst) if rq_lst else None
                db_sess.commit()
                return flask.redirect('/requests')
            if key.startswith('view_profile.'):
                uid = key.split('.')[-1]
                return flask.redirect(f"/profile/{uid}")
        if form.quit_button.data:
            res.set_cookie('user_id', request.cookies.get('user_id'), max_age=0)
            res.headers['location'] = url_for('login')
            return res, 302
        elif form.friends_button.data:
            return flask.redirect('/friends')
        elif form.publics_button.data:
            return flask.redirect('/groups')
        elif form.feed_button.data:
            return flask.redirect('/feed')
        elif form.main_page_button.data:
            return flask.redirect(f'/profile/{user_id}')
        elif form.message_button.data:
            return flask.redirect('/messages')
    if request.method == 'GET':
        return res


@app.route('/messages', methods=['GET', 'POST'])
def messages():
    form = MessagesForm()
    user_id = request.cookies.get('user_id')
    if user_id is None:
        return flask.redirect('/login')
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id)[0]
    if user.friends:
        frs = user.friends.split()
    else:
        frs = []
    frs = db_sess.query(User).filter(User.id.in_(frs))
    res = make_response(
        render_template('messages.html', form=form, title='Сообщения', top_name=user.name, top_surname=user.surname,
                        friends=frs))
    if request.method == 'POST':
        if form.quit_button.data:
            res.set_cookie('user_id', request.cookies.get('user_id'), max_age=0)
            res.headers['location'] = url_for('login')
            return res, 302
        elif form.friends_button.data:
            return flask.redirect('/friends')
        elif form.publics_button.data:
            return flask.redirect('/groups')
        elif form.feed_button.data:
            return flask.redirect('/feed')
        elif form.main_page_button.data:
            return flask.redirect(f'/profile/{user_id}')
        elif form.message_button.data:
            return flask.redirect('/messages')
    elif request.method == 'GET':
        return res


@app.route('/groups', methods=['GET', 'POST'])
def groups():
    form = GroupsForm()
    user_id = request.cookies.get('user_id')
    if user_id is None:
        return flask.redirect('/login')
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id)[0]
    groups = db_sess.query(Group)
    subscriptions = []
    for group in groups:
        tmp = group.subscriptions.split() if group.subscriptions is not None else []
        if user_id in tmp:
            subscriptions.append(group)
    res = make_response(
        render_template('groups.html', form=form, title='Сообщества', top_name=user.name, top_surname=user.surname,
                        groups=subscriptions))
    if request.method == 'POST':
        if form.quit_button.data:
            res.set_cookie('user_id', request.cookies.get('user_id'), max_age=0)
            res.headers['location'] = url_for('login')
            return res, 302
        elif form.friends_button.data:
            return flask.redirect('/friends')
        elif form.publics_button.data:
            return flask.redirect('/groups')
        elif form.feed_button.data:
            return flask.redirect('/feed')
        elif form.main_page_button.data:
            return flask.redirect(f'/profile/{user_id}')
        elif form.message_button.data:
            return flask.redirect('/messages')
        elif form.create_public.data:
            return flask.redirect('/creategroup')
    elif request.method == 'GET':
        return res


@app.route('/creategroup', methods=['GET', 'POST'])
def create_group():
    form = GroupCreateForm()
    res = make_response(render_template('create-group.html', form=form))
    user_id = request.cookies.get('user_id')
    if user_id is None:
        return flask.redirect('/login')
    if request.method == 'POST':
        if form.quit_button.data:
            res.set_cookie('user_id', request.cookies.get('user_id'), max_age=0)
            res.headers['location'] = url_for('login')
            return res, 302
        elif form.friends_button.data:
            return flask.redirect('/friends')
        elif form.publics_button.data:
            return flask.redirect('/groups')
        elif form.feed_button.data:
            return flask.redirect('/feed')
        elif form.main_page_button.data:
            return flask.redirect(f'/profile/{user_id}')
        elif form.message_button.data:
            return flask.redirect('/messages')
        elif form.create_group.data:
            db_sess = db_session.create_session()
            group = Group()
            filename = form.group_avatar.data.filename
            if filename and allowed_file(filename):
                filename = str(len([f for f in os.listdir(os.path.join(app.config['UPLOAD_FOLDER']))]) + 1) + \
                           os.path.splitext(filename)[1]
                form.group_avatar.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if filename == '':
                filename = None
            group.image = filename
            group.author = user_id
            group.name = form.group_name.data
            group.about = form.group_description.data
            db_sess.add(group)
            db_sess.commit()
            gid = group.id
            return flask.redirect(f'groups/{gid}')
    elif request.method == 'GET':
        return res


@app.route('/groups/<group_id>', methods=['GET', 'POST'])
def group(group_id):
    form = GroupViewForm()
    user_id = request.cookies.get('user_id')
    if user_id is None:
        return flask.redirect('/login')
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == int(user_id)).first()
    group = db_sess.query(Group).filter(Group.id == int(group_id)).first()
    g_name = group.name
    if group.subscriptions is not None:
        g_subs = group.subscriptions.split()
    else:
        g_subs = []
    if user_id in g_subs:
        is_subscriptor = True
    else:
        is_subscriptor = False
    tp_name = user.name
    tp_surname = user.surname
    group_author = group.author
    is_auth = group_author == user.id
    posts = db_sess.query(Post).filter(Post.public_id == group_id)
    subscribers = len([i for i in (group.subscriptions.split() if group.subscriptions is not None else [])])
    if not list(posts):
        posts = []
    src = f"../static/img/{group.image}"
    res = make_response(
        render_template('group.html', form=form, top_name=tp_name, top_surname=tp_surname, title=g_name, img_src=src,
                        is_author=is_auth, group_name=g_name, is_sub=is_subscriptor, posts=posts,
                        subscribers=subscribers))
    if request.method == "POST":
        if form.quit_button.data:
            res.set_cookie('user_id', request.cookies.get('user_id'), max_age=0)
            res.headers['location'] = url_for('login')
            return res, 302
        elif form.friends_button.data:
            return flask.redirect('/friends')
        elif form.publics_button.data:
            return flask.redirect('/groups')
        elif form.feed_button.data:
            return flask.redirect('/feed')
        elif form.main_page_button.data:
            return flask.redirect(f'/profile/{user_id}')
        elif form.message_button.data:
            return flask.redirect('/messages')
        elif form.subscribe_button.data:
            group = db_sess.query(Group).filter(Group.id == group_id).first()
            subs_lst = group.subscriptions.split() if group.subscriptions is not None else []
            subs_lst.append(user_id)
            group.subscriptions = ' '.join(subs_lst)
            db_sess.commit()
            return flask.redirect(f"/groups/{group_id}")
        elif form.unsubscribe_button.data:
            group = db_sess.query(Group).filter(Group.id == group_id).first()
            subs_lst = group.subscriptions.split() if group.subscriptions is not None else []
            subs_lst.remove(user_id)
            group.subscriptions = ' '.join(subs_lst)
            db_sess.commit()
            return flask.redirect(f"/groups/{group_id}")
        elif form.send_post.data:
            post_text = request.form['post-text']
            if post_text:
                db_sess = db_session.create_session()
                post = Post()
                post.public_id = group.id
                post.content = post_text
                db_sess.add(post)
                db_sess.commit()
                return flask.redirect(f'/groups/{group_id}')
    elif request.method == "GET":
        return res


@app.route('/message/<uid>', methods=['GET', 'POST'])
def message(uid):
    form = MessageForm()
    user_id = request.cookies.get('user_id')
    if user_id is None:
        return flask.redirect('/login')
    if user_id == uid:
        return flask.redirect('/messages')
    db_sess = db_session.create_session()
    res = db_sess.query(Message)[::-1]
    user = db_sess.query(User).filter(User.id == user_id).first()
    res = make_response(render_template('message.html', form=form, title="Сообщения", messages=res,
                                        user_id=int(user_id), uid=int(uid), top_name=user.name,
                                        top_surname=user.surname))
    if request.method == 'POST':
        if form.quit_button.data:
            res.set_cookie('user_id', request.cookies.get('user_id'), max_age=0)
            res.headers['location'] = url_for('login')
            return res, 302
        elif form.friends_button.data:
            return flask.redirect('/friends')
        elif form.publics_button.data:
            return flask.redirect('/groups')
        elif form.feed_button.data:
            return flask.redirect('/feed')
        elif form.main_page_button.data:
            return flask.redirect(f'/profile/{user_id}')
        elif form.message_button.data:
            return flask.redirect('/messages')
        elif request.form['submit'] == 'Отправить сообщение' and request.form['text'] != '':
            text = request.form['text']
            msg = Message()
            msg.by = int(user_id)
            msg.to = int(uid)
            msg.content = text
            db_sess = db_session.create_session()
            db_sess.add(msg)
            db_sess.commit()
            return flask.redirect(f"/message/{uid}")
        else:
            return res
    elif request.method == 'GET':
        return res


@app.route('/profile/<uid>', methods=['GET', 'POST'])
def profile(uid):
    form = ProfileForm()
    user_id = request.cookies.get('user_id')
    if user_id is None:
        return flask.redirect('/login')
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id)
    profile_id = str(uid)
    user_profile = db_sess.query(User).filter(User.id == profile_id)
    psts = db_sess.query(Post).filter(Post.user_id == int(uid))[::-1]
    if not list(user_profile):
        return "Пользователь не найден"
    user_profile = user_profile[0]
    user = user[0]
    prof_name = user_profile.name
    prof_surname = user_profile.surname
    info = user_profile.about if user_profile.about is not None else 'Этот пользователь не оставил информации о себе.'
    name = user.name if user else ""
    surname = user.surname if user is not None else "Гость"
    is_friends = str(uid) in (user.friends.split() if user.friends is not None else [])

    rq_sent = str(uid) in (user.requests.split() if user.requests is not None else [])
    creation_date = str(user_profile.created_date).split(' ')[0].split('-')
    creation_date = f"{creation_date[2]}.{creation_date[1]}.{creation_date[0]}"
    rq_got = user_id in (user_profile.requests.split() if user_profile.requests is not None else [])
    source = f"../static/img/{user_profile.image}" if user_profile.image is not None else "../static/img/0.jpg"
    res = make_response(
        render_template('profile.html', form=form, title=f'{prof_name} {prof_surname}',
                        top_name=name, top_surname=surname, img_src=source, profile_name=prof_name,
                        profile_surname=prof_surname, about=info, create_date=creation_date, uid=user_id,
                        pid=profile_id, request_sent=rq_sent, friends=is_friends, request_got=rq_got, posts=psts))
    if request.method == 'POST':
        if form.quit_button.data:
            res.set_cookie('user_id', request.cookies.get('user_id'), max_age=0)
            res.headers['location'] = url_for('login')
            return res, 302
        elif form.friends_button.data:
            return flask.redirect('/friends')
        elif form.publics_button.data:
            return flask.redirect('/groups')
        elif form.feed_button.data:
            return flask.redirect('/feed')
        elif form.main_page_button.data:
            return flask.redirect(f'/profile/{user_id}')
        elif form.message_button.data:
            return flask.redirect('/messages')
        elif form.edit_button.data:
            return flask.redirect('/edit_profile')
        elif form.add_friends.data:
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.id == user_id).first()
            requests_list = user.requests.split(' ') if user.requests is not None else []
            requests_list.append(str(uid))
            user.requests = ' '.join(requests_list) if requests_list else None
            db_sess.commit()
            return flask.redirect(f'/profile/{uid}')
        elif form.cancel_request.data:
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.id == user_id).first()
            requests_list = user.requests.split(' ')
            requests_list.remove(uid)
            user.requests = ' '.join(requests_list) if requests_list else None
            db_sess.commit()
            return flask.redirect(f'/profile/{uid}')
        elif form.remove_friends.data:
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.id == user_id).first()
            friends_list = user.friends.split(' ')
            friends_list.remove(uid)
            user.friends = ' '.join(friends_list) if friends_list else None
            db_sess.commit()
            return flask.redirect(f'/profile/{uid}')
        elif form.write_message.data:
            return flask.redirect(f"/message/{uid}")
        elif form.accept_rq.data:
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.id == uid).first()
            rqs = user.requests.split() if user.requests is not None else []
            rqs.remove(user_id)
            frs = user.friends.split() if user.friends is not None else []
            frs.append(user_id)
            user.friends = ' '.join(frs) if frs else None
            user.requests = ' '.join(rqs) if rqs else None
            main_user = db_sess.query(User).filter(User.id == user_id).first()
            frs = main_user.friends.split() if main_user.friends is not None else []
            frs.append(uid)
            main_user.friends = ' '.join(frs) if frs else None
            db_sess.commit()
            return flask.redirect(f"/profile/{uid}")
        elif form.decline_rq.data:
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.id == uid).first()
            rqs = user.requests.split() if user.requests is not None else None
            rqs.remove(user_id)
            user.requests = ' '.join(rqs) if rqs else None
            db_sess.commit()
            return flask.redirect(f"/profile/{uid}")
        elif form.send_post.data:
            post_text = request.form['post-text']
            if post_text:
                db_sess = db_session.create_session()
                post = Post()
                post.user_id = uid
                post.content = post_text
                db_sess.add(post)
                db_sess.commit()
                return flask.redirect(f"/profile/{uid}")
            else:
                return flask.redirect(f"/profile/{uid}")
        else:
            return flask.abort(404)
    elif request.method == 'GET':
        return res


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    form = EditForm()
    db_sess = db_session.create_session()
    user_id = request.cookies.get('user_id')
    if user_id is None:
        return flask.redirect('/login')
    user = db_sess.query(User).filter(User.id == user_id)[0]
    name = user.name
    surname = user.surname
    res = make_response(
        render_template("profile_edit.html", form=form, prev_name=name, prev_surname=surname, top_name=name,
                        top_surname=surname))
    if request.method == 'POST':
        if form.quit_button.data:
            res.set_cookie('user_id', request.cookies.get('user_id'), max_age=0)
            res.headers['location'] = url_for('login')
            return res, 302
        elif form.friends_button.data:
            return flask.redirect('/friends')
        elif form.publics_button.data:
            return flask.redirect('/groups')
        elif form.feed_button.data:
            return flask.redirect('/feed')
        elif form.main_page_button.data:
            user_id = request.cookies.get('user_id')
            return flask.redirect(f'/profile/{user_id}')
        elif form.message_button.data:
            return flask.redirect('/messages')
        return res
    elif request.method == 'GET':
        return res


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    app.run(host='localhost', port=5000)
