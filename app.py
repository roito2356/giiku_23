import os
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    abort,
    jsonify,
)
from flask_wtf import FlaskForm
from wtforms import ValidationError, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from pytz import timezone
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.config["SECRET_KEY"] = "mysecretkey"  # セッションのセキュリティキー
basedir = os.path.abspath(os.path.dirname(__file__))  # データベースにURLで繋げるためにディレクトリのパスを取得する
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "data.sqlite"
)  # SQLiteへ繋げる
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)  # SQLAlchemyをインスタンス化する
Migrate(app, db)  # データベースを管理
# flask db initで、"migrations"フォルダが作成される
# データベース操作：
# 差分確認コマンドflask db migrate
# データベースに反映：flask db upgrade

# ログインマネージャーの設定
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# ログイン権限のフラッシュメッセージの設定
def localize_callback(*args, **kwargs):
    return "このページにアクセスするには、ログインが必要です。"


login_manager.localize_callback = localize_callback


# ログイン管理関数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# リレーショナルデータベース start
from sqlalchemy.engine import Engine
from sqlalchemy import event


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# リレーショナルデータベース end

########
# テーブルのモデルを定義
########


# ユーザーテーブルを型定義
class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    administrator = db.Column(db.String(1))
    comprel = db.relationship(
        "Complete", backref="author", lazy="dynamic"
    )  # リレーショナルデータベースの設定　(users)1対(complete)多

    def __init__(self, email, username, password, administrator):  # 初期化の処理(プロバティの設定)
        self.email = email
        self.username = username
        self.password = password
        self.administrator = administrator

    def __repr__(self):  # printでターミナルに出力したときにreturnの内容を呼び出すことができる
        return f"UserName: {self.username}"

    def check_password(
        self, password
    ):  # ハッシュ化されたパスワードのチェック　※データベースのパスワードはハッシュ化されていないとチェックできない
        # print(self, password, check_password_hash(self.password_hash, password))
        return check_password_hash(self.password_hash, password)

    @property  # パスワードの値を直接参照できないようにする
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter  # 入力されたpasswordをハッシュ化する
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def is_administrator(self):  # 管理者か判定
        if self.administrator == "1":
            return 1
        else:
            return 0


# # 評価テーブルを型定義
class Complete(db.Model):
    __tablename__ = "complete"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )  # リレーショナルデータベースの設定"db.ForeignKey("users.id")"
    date = db.Column(db.DateTime, default=datetime.now(timezone("Asia/Tokyo")))
    evaluation = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(200), nullable=False)

    def __init__(self, user_id, evaluation, comment):
        self.evaluation = evaluation
        self.comment = comment
        self.user_id = user_id

    def __repr__(self):  # printでターミナルに出力したときにreturnの内容を呼び出すことができる
        return f"completeID: {self.id}, Evaluation: {self.evaluation}, Author: {self.author} \n"


########
# フォームのモデルを定義
########


# ログインフォームの型定義
class LoginForm(FlaskForm):
    email = StringField(
        "Email", validators=[DataRequired(), Email(message="正しいメールアドレスを入力してください")]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("ログイン")


# with app.app_context():
#     db.create_all()


# ユーザー登録フォームの型定義
class RegistrationForm(FlaskForm):
    email = StringField(
        "メールアドレス", validators=[DataRequired(), Email(message="正しいメールアドレスを入力してください")]
    )
    username = StringField("ユーザー名", validators=[DataRequired()])
    password = PasswordField(
        "パスワード",
        validators=[DataRequired(), EqualTo("pass_confirm", message="パスワードが一致していません")],
    )
    pass_confirm = PasswordField("パスワード(確認)", validators=[DataRequired()])
    submit = SubmitField("登録")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("入力されたメールアドレスは既に登録されています。")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("入力されたユーザー名は既に使われています。")


# ユーザー更新フォームの型定義
class UpdateUserForm(FlaskForm):
    email = StringField(
        "メールアドレス", validators=[DataRequired(), Email(message="正しいメールアドレスを入力してください")]
    )
    username = StringField("ユーザー名", validators=[DataRequired()])
    password = PasswordField(
        "パスワード", validators=[EqualTo("pass_confirm", message="パスワードが一致していません。")]
    )
    pass_confirm = PasswordField("パスワード(確認)")
    submit = SubmitField("更新")

    def __init__(self, user_id, *args, **kwargs):
        super(UpdateUserForm, self).__init__(*args, **kwargs)
        self.id = user_id

    def validate_email(self, field):
        if User.query.filter(User.id != self.id).filter_by(email=field.data).first():
            raise ValidationError("入力されたメールアドレスは既に登録されています。")

    def validate_username(self, field):
        if User.query.filter(User.id != self.id).filter_by(username=field.data).first():
            raise ValidationError("入力されたユーザー名は既に使われています。")


########
# View関数を作成
########


# テスト用View関数
@app.route("/test")
def test():
    return render_template("materials/material/dice1/index.html")


# topページ(教材一覧)View関数
@app.route("/")
def top():
    return render_template("materials/materials_list.html")


# ユーザー登録ページView関数
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # session["email"] = form.email.data
        # session["username"] = form.username.data
        # session["password"] = form.password.data
        user = User(
            email=form.email.data,
            username=form.username.data,
            password=form.password.data,
            administrator="0",
        )
        db.session.add(user)
        db.session.commit()
        flash("ユーザーが登録されました")  # フラッシュメッセージ
        return redirect(url_for("login"))
    return render_template("users/register.html", form=form)


# マイページView関数
@app.route("/mypage")
@login_required
def mypage():
    return render_template("users/mypage.html")


# ログインView関数
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            if user.check_password(form.password.data):
                login_user(user)
                next = request.args.get("next")
                if next == None or not next[0] == "/":
                    # 管理者の場合ユーザー管理ページへそれ以外はMypageへ
                    if current_user.is_administrator():
                        next = url_for("user_maintenance")
                    else:
                        next = url_for("mypage")
                return redirect(next)
            else:
                flash("パスワードが一致しません")
        else:
            flash("入力されたユーザーは存在しません")

    return render_template("users/login.html", form=form)


# ログアウトView関数
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# ユーザー管理View関数
@app.route("/user_maintenance")
@login_required
def user_maintenance():
    # 管理者で無い場合403エラー
    if not current_user.is_administrator():
        abort(403)
    page = request.args.get("page", 1, type=int)
    users = User.query.order_by(User.id).paginate(page=page, per_page=10)
    return render_template("users/user_maintenance.html", users=users)


# ユーザー更新View関数
@app.route("/<int:user_id>/accountup", methods=["GET", "POST"])
@login_required
def accountup(user_id):
    user = User.query.get_or_404(user_id)
    # 自分のユーザか管理者では無い場合403エラー
    if user.id != current_user.id and not current_user.is_administrator():
        abort(403)
    form = UpdateUserForm(user_id)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        if form.password.data:
            user.password = form.password.data
        db.session.commit()
        flash("ユーザーアカウントが更新されました")
        return redirect(url_for("mypage"))
    elif request.method == "GET":
        form.username.data = user.username
        form.email.data = user.email
    return render_template("users/accountup.html", form=form)


# ユーザー削除View関数
@app.route("/<int:user_id>/delete", methods=["GET", "POST"])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    # 管理者では無い場合403エラー
    if not current_user.is_administrator():
        abort(403)
    if user.is_administrator():
        flash("管理者は削除できません")
        return redirect(url_for("accountup", user_id=user_id))
    db.session.delete(user)
    db.session.commit()
    flash("ユーザーアカウントが削除されました")
    return redirect(url_for("user_maintenance"))


# 403エラーページの追加
@app.errorhandler(403)
def error_403(error):
    return render_template("error_pages/403.html"), 403


# 404エラーページの追加
@app.errorhandler(404)
def error_404(error):
    return render_template("error_pages/404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
