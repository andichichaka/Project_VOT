from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
import requests
from sqlalchemy import create_engine, select, Text, update
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column

app = Flask(__name__)
CORS(app)

db_host = "localhost"

keycloak_host = "localhost"
realm_id = "myrealm"
client_id = "backend"
client_secret = "secret"

def create_db_engine():
    return create_engine(f"mariadb+pymysql://user:password@{db_host}:3306/database")


class Base(DeclarativeBase):
    pass

class BlogPost(Base):
    __tablename__ = 'blog_post'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)

@app.route('/posts', methods=['GET'])
def get_posts():
    engine = create_db_engine()

    with Session(engine) as session:
        posts = session.scalars(select(BlogPost))
        result = []
        for post in posts:
            result.append({'id': post.id, 'content': post.content, 'user_id': post.user_id})
    return jsonify(result), 200

@app.route('/post', methods=['POST'])
def create_post():
    data = request.json
    content = data['content']
    token = data['token']
    response = requests.post(f"http://{keycloak_host}:8080/realms/{realm_id}/protocol/openid-connect/token/introspect", {"client_id": client_id, "client_secret": client_secret, "token": token}).json()

    if not response.get("active"):
        return make_response({"message": "Unauthorized"}, 401)
    
    new_post = BlogPost(user_id=response["sub"], content=content)
    engine = create_db_engine()

    with Session(engine) as session:
        session.add(new_post)
        session.commit()
    return jsonify({'msg': 'Post created successfully'}), 201

@app.route('/post/<int:post_id>', methods=['PUT'])
def edit_post(post_id):
    data = request.json
    content = data['content']
    token = data['token']
    response = requests.post(f"http://{keycloak_host}:8080/realms/{realm_id}/protocol/openid-connect/token/introspect", {"client_id": client_id, "client_secret": client_secret, "token": token}).json()

    if not response.get("active"):
        return make_response({"message": "Unauthorized"}, 401)

    user_id = response.get("sub")
    engine = create_db_engine()

    with Session(engine) as session:
        post = session.get(BlogPost, post_id)
        if post and post.user_id == user_id:
            post.content = content
            session.commit()
            return jsonify({'msg': 'Post updated successfully'}), 200
        else:
            return make_response({"message": "Unauthorized or Post not found"}, 403)

Base.metadata.create_all(create_db_engine())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)