#  coding:utf-8
from . import home
from flask import render_template, redirect, url_for, flash, request, session, Response
from app.home.forms import RegistForm, LoginForm, UserdetailForm, PwdForm, CommentForm
from app.models import User, Userlog, Comment, Movie, Moviecol, Tag, Preview
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from app import db, app, rd
from functools import wraps
import os, time, json, uuid
from datetime import datetime


def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]
    return filename


def admin_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("user.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


@admin_login_req
@home.route('/<int:page>/', methods=['GET'])
def index(page=None):
    tags = Tag.query.all()
    page_data = Movie.query
    tid = request.args.get("tid", 0)
    # 评论
    if int(tid) != 0:
        page_data = page_data.filter_by(tag_id=int(tid))
    # 星级
    star = request.args.get("star", 0)
    if int(star) != 0:
        page_data = page_data.filter_by(star=int(star))
    # 播放量
    pn = request.args.get("pn", 0)
    if int(pn) != 0:
        if int(pn) == 1:
            page_data = page_data.order_by(Movie.playnum.desc())
        else:
            page_data = page_data.order_by(Movie.playnum.asc())
    # 评论量
    cn = request.args.get("cn", 0)
    if int(cn) != 0:
        if int(cn) == 1:
            page_data = page_data.order_by(Movie.commentnum.desc())
        else:
            page_data = page_data.order_by(Movie.commentnum.asc())
    # 上映时间
    rt = request.args.get("rt", 0)
    if int(rt) != 0:
        if int(rt) == 1:
            page_data = page_data.order_by(Movie.release.desc())
        else:
            page_data = page_data.order_by(Movie.release.asc())

    if page is None:
        page = 1
    page_data = page_data.paginate(page=page, per_page=12)
    p = dict(
        tid=tid,
        star=star,
        pn=pn,
        cn=cn,
        rt=rt,
    )
    return render_template("home/index.html", p=p, tags=tags, page_data=page_data)


@home.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(name=data['name']).first()
        if not user.check_pwd(data['pwd']):
            flash("密码错误", "err")
            return redirect(url_for("home.login"))
        session['user'] = user.name
        session['user_id'] = user.id

        userlog = Userlog(
            user_id=user.id,
            ip=request.remote_addr
        )
        db.session.add(userlog)
        db.session.commit()
        flash("登录成功", "ok")
        return redirect(url_for("home.user"))

    return render_template("home/login.html", form=form)


@home.route('/logout/')
def logout():
    session.pop("user", None)
    session.pop("user_id", None)
    return redirect(url_for("home.login"))


@admin_login_req
@home.route('/regist/', methods=['GET', 'POST'])
def regist():
    form = RegistForm()
    if form.validate_on_submit():
        data = form.data
        user = User(
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            pwd=generate_password_hash(data["pwd"]),
            uuid=uuid.uuid4().hex
        )
        db.session.add(user)
        db.session.commit()
        flash("注册成功", "ok")
        redirect(url_for("home.regist"))
        userlog = Userlog(
            user_id=user.id,
            ip=request.remote_addr
        )
        db.session.add(userlog)
        db.session.commit()
    return render_template("home/regist.html", form=form)


@admin_login_req
@home.route('/user/', methods=['GET', 'POST'])
def user():
    form = UserdetailForm()
    user = User.query.get_or_404(int(session['user_id']))
    if request.method == "GET":
        form.name.data = user.name
        form.email.data = user.email
        form.phone.data = user.phone
        form.info.data = user.info
        form.face.validators = []

    if form.validate_on_submit():
        data = form.data
        name_count = User.query.filter_by(name=data['name']).count()
        phone_count = User.query.filter_by(name=data['phone']).count()
        email_count = User.query.filter_by(name=data['email']).count()
        if not os.path.exists(app.config['USER_DIR']):
            os.makedirs(app.config["USER_DIR"])
            os.chmod(app.config["USER_DIR"], 'rw')

        if form.face.data.filename != "":
            file_logo = secure_filename(form.face.data.filename)
            user.face = change_filename(file_logo)
            form.face.data.save(app.config["USER_DIR"] + user.face)

        if email_count == 1 and user.email != data['email']:
            flash("用户邮箱已存在", "err")
            return redirect(url_for("home.user"))
        if phone_count == 1 and user.email != data['phone']:
            flash("用户手机已存在", "err")
            return redirect(url_for("home.user"))
        if name_count == 1 and user.name != data['name']:
            flash("用户昵称已存在", "err")
            return redirect(url_for("home.user"))
        user.name = data["name"]
        user.email = data["email"]
        user.phone = data["phone"]
        user.info = data["info"]

        db.session.add(user)
        db.session.commit()
        flash("用户资料修改成功", "ok")
    return render_template("home/user.html", form=form, user=user)


@admin_login_req
@home.route('/pwd/', methods=['GET', "POST"])
def pwd():
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        print('0')
        user = User.query.filter_by(id=session['user_id']).first()
        if not user.check_pwd(data['old_pwd']):
            print('1')
            flash("旧密码错误", 'err')
            return redirect(url_for('home.pwd'))
        if data['old_pwd'] == data['new_pwd']:
            flash("新旧密码相同", 'err')
            return redirect(url_for('home.pwd'))
        print('3')
        user.pwd = generate_password_hash(data['new_pwd'])
        db.session.add(user)
        db.session.commit()
        flash("修改密码成功，请重新登录", 'ok')
        return redirect(url_for('home.login'))
    return render_template("home/pwd.html", form=form)


@admin_login_req
@home.route('/comments/<int:page>/', methods=['GET'])
def comments(page=None):
    if page is None:
        page = 1
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Comment.movie_id,
        User.id == Comment.user_id
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("home/comments.html", page_data=page_data)


@admin_login_req
@home.route('/loginlog/<int:page>/', methods=['GET'])
def loginlog(page=None):
    if page is None:
        page = 1
    page_data = Userlog.query.join(
        User
    ).filter(
        User.id == Userlog.user_id
    ).order_by(
        Userlog.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("home/loginlog.html", page_data=page_data)


@admin_login_req
@home.route('/moviecol/add/', methods=['GET'])
def moviecol_add():
    mid = request.args.get("mid", "")
    uid = request.args.get("uid", "")
    col_count = Moviecol.query.filter(
        Moviecol.movie_id == int(mid),
        Moviecol.user_id == int(uid)
    ).count()
    if col_count == 1:
        data = dict(ok=0)
    if col_count == 0:
        moviecol = Moviecol(
            user_id=uid,
            movie_id=mid,
        )
        db.session.add(moviecol)
        db.session.commit()
        data = dict(ok=1)
    return json.dumps(data)


@admin_login_req
@home.route('/moviecol/<int:page>/', methods=['GET'])
def moviecol(page=None):
    if page is None:
        page = 1
    page_data = Moviecol.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Moviecol.movie_id,
        User.id == session['user_id']
    ).order_by(
        Moviecol.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("home/moviecol.html", page_data=page_data)


@admin_login_req
@home.route('/animation/', methods=['GET'])
def animation():
    preview_data = Preview.query.all()
    return render_template("home/animation.html", preview_data=preview_data)


@admin_login_req
@home.route('/search/<int:page>/', methods=['GET'])
def search(page=None):
    if page is None:
        page = 1
    key = request.args.get("key", "")
    movie_count = Movie.query.filter(Movie.title.ilike("%" + key + "%")).count()
    page_data = Movie.query.filter(
        Movie.title.ilike("%" + key + "%")
    ).order_by(
        Movie.addtime.desc()
    ).paginate(page=page, per_page=10)
    page_data.key = key
    return render_template("home/search.html", movie_count=movie_count, page_data=page_data)


@admin_login_req
@home.route('/play/<int:id>/<int:page>', methods=['GET', 'POST'])
def play(id=None, page=None):
    form = CommentForm()

    movie = Movie.query.join(
        Tag
    ).filter(
        Tag.id == Movie.tag_id,
        Movie.id == int(id)
    ).first_or_404()

    if request.method == "GET":
        movie.playnum += 1
        db.session.add(movie)
        db.session.commit()

    if page is None:
        page = 1
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == id,
        User.id == Comment.user_id
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=10)

    if form.validate_on_submit():
        data = form.data
        comment = Comment(
            content=data['content'],
            movie_id=id,
            user_id=session['user_id']
        )

        db.session.add(comment)
        db.session.commit()
        flash("提交评论成功", "ok")
        return redirect(url_for("home.play", page=1, id=id))
    return render_template("home/play.html", form=form, page_data=page_data, movie=movie)


@admin_login_req
@home.route('/video/<int:id>/<int:page>', methods=['GET', 'POST'])
def video(id=None, page=None):
    form = CommentForm()

    movie = Movie.query.join(
        Tag
    ).filter(
        Tag.id == Movie.tag_id,
        Movie.id == int(id)
    ).first_or_404()

    if request.method == "GET":
        movie.playnum += 1
        db.session.add(movie)
        db.session.commit()

    if page is None:
        page = 1
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == id,
        User.id == Comment.user_id
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=10)

    if form.validate_on_submit():
        data = form.data
        comment = Comment(
            content=data['content'],
            movie_id=id,
            user_id=session['user_id']
        )

        db.session.add(comment)
        db.session.commit()
        flash("提交评论成功", "ok")
        return redirect(url_for("home.video", page=1, id=id))
    return render_template("home/video.html", form=form, page_data=page_data, movie=movie)


# 处理弹幕消息
@home.route("/dm/v3/", methods=["GET", "POST"])
def dm():
    import json
    if request.method == "GET":
        # 获取弹幕消息队列
        mid = request.args.get("id")
        key = "movie" + str(mid)
        if rd.llen(key):
            msgs = rd.lrange(key, 0, 2999)
            res = {
                "code": 0,
                "data": [json.loads(v) for v in msgs]
            }
        else:
            res = {
                "code": 1,
                "danmaku": []
            }
        resp = json.dumps(res)
    if request.method == "POST":
        # 添加弹幕
        data = json.loads(request.get_data())
        msg = {
            "__v": 0,
            "_id": datetime.now().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex,
            "author": data["author"],
            "time": data["time"],
            "text": data["text"],
            "color": data["color"],
            "type": data["type"],
            "ip": request.remote_addr,
            "player": data["id"]
        }
        res = {
            "code": 0,
            "danmaku": msg
        }
        resp = json.dumps(res)
        msg = [data["time"], data["type"], data["color"], data["author"], data["text"]]
        rd.lpush("movie" + str(data["id"]), json.dumps(msg))
    return Response(resp, mimetype="application/json")
