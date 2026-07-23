from flask import Flask, jsonify, request 
from flask_login import login_required,logout_user,login_user, LoginManager,UserMixin, current_user
from dotenv import load_dotenv                   
import os
import bcrypt                                    
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session  

app = Flask(__name__)
load_dotenv()
app.secret_key = os.environ.get("SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("SECRET_KEY not set in .env")

login_manager = LoginManager()
login_manager.init_app(app)

engine = create_engine("sqlite:///apprentice_log.db")
class Base(DeclarativeBase):
    pass

class User(Base,UserMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email:Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str] 

class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id:Mapped[int] = mapped_column(ForeignKey("users.id"))
    filename: Mapped[str]
    content: Mapped[str]


class Chunk(Base):
    __tablename__ = "chunks"
    id: Mapped[int] = mapped_column(primary_key=True)
    document_id:Mapped[int] = mapped_column(ForeignKey("documents.id"))
    chunk_index:Mapped[int]
    content:Mapped[str]
    embedding: Mapped[str | None] = mapped_column(nullable=True)

Base.metadata.create_all(engine)

def chunk_paragraphs(text):
    text = text.replace("\r\n", "\n")

    paragraphs = text.split("\n\n")

    chunks = []

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if paragraph:
            chunks.append(paragraph)

    return chunks


def chunk_python(text):
    text = text.replace("\r\n", "\n")
    lines = text.split("\n")

    chunks = []
    curr_chunk = []

    for line in lines:
        if (line.startswith("class ") or line.startswith("def ")):

            
            if curr_chunk:
                chunks.append("\n".join(curr_chunk))

            
            curr_chunk = [line]

        else:
           curr_chunk.append(line)


    
    if curr_chunk:
        chunks.append("\n".join(curr_chunk))

    
    return chunks




@login_manager.user_loader
def load_user(user_id):
    with Session(engine) as session:
        return session.get(User, int(user_id))

@app.route("/register", methods = ["POST"])
def register():
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({
            "status": "error",
            "message": "Email and password are required."
        }), 400

    email = data["email"]
    password = data["password"]
    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()).decode('utf-8')

    with Session(engine) as session:
        if  session.query(User).filter_by(email=email).first():
            return jsonify({"status":"error","message":"Email already exists."}),409
        session.add(User(email=email,password_hash=password_hash))
        session.commit()

    return jsonify({"status":"success","message":"Account created."}),201

@app.route("/login", methods = ["POST"])
def login():
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({
            "status": "error",
            "message": "Email and password are required."
        }), 400
    email = data["email"]
    password = data["password"]
    with Session(engine) as session:
        user = session.query(User).filter_by(email=email).first()

        if  not user :
            return jsonify({
            "status": "error",
            "message": "Invalid email or password."
            }), 401
        if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
            return jsonify({
            "status": "error",
            "message": "Invalid email or password."
            }), 401
        login_user(user)
    return jsonify({
        "status": "success",
        "message": "Login successful."
    })

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"status": "success", "message": "Logged out successfully."})

@app.route("/upload", methods=["POST"])
@login_required
def upload():
    if "file" not in request.files:
        return jsonify({
            "status": "error",
            "message": "No file uploaded."
        }), 400


    file = request.files["file"]

    try:
        content = file.read().decode("utf-8")
    except UnicodeDecodeError:
        return jsonify({
            "status": "error",
            "message": "File must be UTF-8 text."
        }), 400
    if not content.strip():
        return jsonify({
            "status": "error",
            "message": "File is empty."
        }), 400

    if file.filename.endswith(".py"):
        chunks = chunk_python(content)
    elif file.filename.endswith(".txt") or file.filename.endswith(".md"):
        chunks = chunk_paragraphs(content)
    else:
        return jsonify({
            "status": "error",
            "message": "Unsupported file type."
        }), 400

    
    document = Document(
        user_id=current_user.id,
        filename=file.filename,
        content=content
    )

    with Session(engine) as session:
        session.add(document)
        session.flush()

        for index,chunk in enumerate(chunks):
            chunk_row = Chunk(
                document_id = document.id,
                chunk_index= index,
                content=chunk,
                embedding=None
            )
            session.add(chunk_row)

        session.commit()

        return jsonify({
            "status": "success",
            "document_id": document.id,
            "chunk_count": len(chunks)
        }), 201

if __name__ == "__main__":
    app.run(debug=True)