# 最初にUserデータベースに保存するユーザー
from app import db, User
from werkzeug.security import generate_password_hash

# db.drop_all() #同じデータをサイド保存するときはデータを削除しないとエラーがでる　※Migrateで解決できる
db.create_all()

password = "123"
# パスワードのハッシュ化
password_hash = generate_password_hash(password)

user1 = User(
    email="admin_user@test.com",
    username="Admin User",
    password_hash=password_hash,
    administrator="1",
)
user2 = User("test_user1@test.com", "test User1", "111", "0")

db.session.add_all([user1, user2])
db.session.commit()

# print(user1.id)
# print(user2.id)
