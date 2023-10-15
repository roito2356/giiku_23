from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "your_secret_key"  # セッションのセキュリティキー
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)


# ユーザーモデルを定義
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Complete(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    evaluation = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

# テスト用View関数
@app.route("/test")
def test():
    return render_template("materials/material/dice1/index.html")

# topページ(教材一覧)View関数
@app.route("/")
def top():
    return render_template("materials/materials_list.html")

# マイページView関数
@app.route("/mypage")
def mypage():
    if 'id' in session:
        return render_template("users/mypage.html")
    else:
        return render_template("users/login.html")

# ユーザー登録ページView関数
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        name = request.form['exampleInputuser1']
        email = request.form['exampleInputEmail1']
        password = request.form['inputPassword5']

        existing_user_name = User.query.filter_by(name=name).first()
        existing_user_email = User.query.filter_by(email=email).first()

        if existing_user_name or existing_user_email:
            # ユーザー名がすでに存在する場合はエラーメッセージを表示
            return render_template('users/register.html')
        
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('users/register.html')

# ログイン機能
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name_email = request.form['name_email']
        password = request.form['password']

        user = User.query.filter((User.name == name_email or User.email == name_email) & (User.password == password)).first()

        if user:
            session['id'] = user.id
            # ログインに成功した場合は/mypageにリダイレクト
            return redirect(url_for('mypage'))
        else:
            # ログインに失敗した場合はlogin.htmlにリダイレクト
            return redirect(url_for('login')) #ログイン失敗的なメッセージ

    return render_template('users/login.html')






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
