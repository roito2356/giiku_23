from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# app.secret_key = "your_secret_key"  # セッションのセキュリティキー
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///login.db"
# db = SQLAlchemy(app)


# # ユーザーモデルを定義
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     password = db.Column(db.String(120), nullable=False)


# マイページView関数
@app.route("/mypage")
def mypage():
    return render_template("users/mypage.html")


# topページ(教材一覧)View関数
@app.route("/")
def top():
    return render_template("top-page.html")


# ユーザー登録ページView関数
@app.route("/register", methods=["GET", "POST"])
def register():
    return render_template("users/register.html")


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
