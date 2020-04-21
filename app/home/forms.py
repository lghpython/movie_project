# coding:utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email, Regexp, EqualTo, ValidationError
from app.models import User


class RegistForm(FlaskForm):
    name = StringField(
        label="昵称",
        validators=[
            DataRequired("请输入昵称！")
        ],
        description="昵称",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "昵称"
        }
    )
    email = StringField(
        label="邮箱",
        validators=[
            DataRequired("请输入邮箱！"),
            Email("邮箱格式不正确")
        ],
        description="邮箱",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "邮箱"
        }
    )
    phone = StringField(
        label="手机",
        validators=[
            DataRequired("请输入手机！"),
            Regexp(r"1[3578]\d{9}")
        ],
        description="手机",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "手机"
        }
    )

    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired("请输入密码！")
        ],
        description="密码",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入密码！"
        }
    )

    repwd = PasswordField(
        label="确认密码",
        validators=[
            DataRequired("请再次输入密码！"),
            EqualTo('pwd', "输入密码不一致！")

        ],
        description="确认密码",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请再次输入密码！"
        }
    )

    submit = SubmitField(
        label="注册",
        render_kw={
            "class": "btn btn-lg btn-success btn-block"
        }
    )

    def validate_name(self, field):
        name = field.data
        name_count = User.query.filter_by(name=name).count()
        if name_count == 1:
            raise ValidationError("昵称已存在！")

    def validate_mail(self, field):
        email = field.data
        email_count = User.query.filter_by(email=email).count()
        if email_count == 1:
            raise ValidationError("邮箱已存在！")

    def validate_phone(self, field):
        phone = field.data
        phone_count = User.query.filter_by(phone=phone).count()
        if phone_count == 1:
            raise ValidationError("手机号码已存在！")


class LoginForm(FlaskForm):
    name = StringField(
        label="账号",
        validators=[
            DataRequired("请输入账号！")
        ],
        description="账号",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "账号"
        }
    )

    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired("请输入密码！")
        ],
        description="密码",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入密码！"
        }
    )

    submit = SubmitField(
        label="登录",
        render_kw={
            "class": "btn btn-lg btn-success btn-block"
        }
    )

    def validate_name(self, field):
        name = field.data
        name_count = User.query.filter_by(name=name).count()
        if name_count == 0:
            raise ValidationError("账号不存在！")


class UserdetailForm(FlaskForm):
    name = StringField(
        label="昵称",
        validators=[
            DataRequired("请输入昵称！")
        ],
        description="昵称",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "昵称",
            "autofocus": "autofocus"
        }
    )
    email = StringField(
        label="邮箱",
        validators=[
            DataRequired("请输入邮箱！"),
            Email("邮箱格式不正确")
        ],
        description="邮箱",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "邮箱",
            "autofocus": "autofocus"
        }
    )
    phone = StringField(
        label="手机",
        validators=[
            DataRequired("请输入手机！"),
            Regexp(r"1[3578]\d{9}")
        ],
        description="手机",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "手机",
            "autofocus": "autofocus"
        }
    )

    face = FileField(
        label="头像",
        validators=[
            DataRequired("请上传头像！")
        ],
        description="头像"
    )

    info = TextAreaField(
        label="简介",
        validators=[
            DataRequired("请输入简介")
        ],
        description="简介",
        render_kw={
            "class": "form-control",
            "rows": "10",
        }
    )

    submit = SubmitField(
        label='保存修改',

        render_kw={
            "href": "user.html",
            "class": "btn btn-success"
        }
    )


class PwdForm(FlaskForm):
    old_pwd = PasswordField(
        label='旧密码',
        validators=[
            DataRequired("请输入旧密码！")
        ],
        description='旧密码',
        render_kw={
            "class": "form-control",
            "placeholder": "请输入旧密码！",
            'required': "required"

        }
    )

    new_pwd = PasswordField(
        label='新密码',
        validators=[
            DataRequired("请输入新密码！"),

        ],
        description='新密码',
        render_kw={
            "class": "form-control",
            "placeholder": "请输入新密码！",
            'required': "required"

        }
    )

    submit = SubmitField(
        '修改密码',
        render_kw={
            "class": "btn btn-success"
        }
    )


class CommentForm(FlaskForm):
    content = TextAreaField(
        label="内容",
        validators=[
            DataRequired("请输入评论内容")
        ],
        description="内容",
        render_kw={
            "id": "input_content",
            "rows": "10"
        }
    )

    submit = SubmitField(
        label='提交评论',
        render_kw={
            "class": "btn btn-success",
            "id": "btn-sub"
        }
    )
