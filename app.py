from flask import Flask, jsonify, request,render_template
from flask_login import login_required,logout_user,login_user, LoginManager,UserMixin, current_user
from dotenv import load_dotenv                   
import os
import bcrypt                                    
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session  
from google import genai
import math
import json




app = Flask(__name__)
load_dotenv()


client = genai.Client(api_key=os.environ.get("API_KEY"))


app.secret_key = os.environ.get("SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("SECRET_KEY not set in .env")

login_manager = LoginManager()
login_manager.init_app(app)

db_url = os.environ.get(
    "DATABASE_URL",
    "sqlite:///apprentice_log.db"
)

if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(db_url)
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

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))

    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(y * y for y in b))

    if mag_a == 0 or mag_b == 0:
        return 0

    return dot / (mag_a * mag_b)



def chunk_paragraphs(text):
    text = text.replace("\r\n", "\n")

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks = []
    current = ""

    for paragraph in paragraphs:
        lines = paragraph.split("\n")
        first = lines[0].strip()

     
        if first.startswith("#"):
            if current:
                chunks.append(current.strip())
            current = paragraph
            continue

     
        if first.startswith("-") or first.startswith("*"):
            if current:
                current += "\n\n" + paragraph
            else:
                current = paragraph
            continue

      
        if len(paragraph) < 100:
            if current:
                current += "\n\n" + paragraph
            else:
                current = paragraph
            continue

       
        if current:
            chunks.append(current.strip())

        current = paragraph

    if current:
        chunks.append(current.strip())

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
    
    

    with Session(engine) as session:
        document = Document(
                user_id=current_user.id,
                filename=file.filename,
                content=content
        )
        session.add(document)
        session.flush()

        try:
            result = client.models.embed_content(
                model="gemini-embedding-001",
                contents=chunks,
                config={"task_type": "RETRIEVAL_DOCUMENT"}
            )
        except Exception:
            session.rollback()
            return jsonify({
                "status": "error",
                "message": "Failed to generate embeddings."
            }), 500

        for index,chunk in enumerate(chunks):
            chunk_row = Chunk(
                document_id = document.id,
                chunk_index= index,
                content=chunk,
                embedding=json.dumps(result.embeddings[index].values)
            )
            session.add(chunk_row)

        session.commit()

        return jsonify({
            "status": "success",
            "document_id": document.id,
            "chunk_count": len(chunks)
        }), 201

def retrieve(question,user_id,k=3):
    with Session(engine) as session:
        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=question,
            config={"task_type": "RETRIEVAL_QUERY"}
        )

        ques_vector = result.embeddings[0].values

        chunks = (
            session.query(Chunk,Document.filename)
            .join(Document)
            .filter(Document.user_id == user_id)
            .all()
        )

        scored_chunks = []

        for chunk,filename in chunks:
            if chunk.embedding is None:
                continue

            chunk_vector = json.loads(chunk.embedding)
            score = cosine(ques_vector,chunk_vector)
            scored_chunks.append((score,chunk,filename))

        scored_chunks.sort(
            key=lambda x: x[0],
            reverse=True
        )
        return scored_chunks[:k]

@app.route("/ask", methods=["POST"])
@login_required
def ask():
    data = request.get_json()

    if not data or "question" not in data:
        return jsonify({
            "status": "error",
            "message": "Question is required."
        }), 400

    question = data["question"]

    
    results = retrieve(
        question,
        current_user.id,
        k=3
    )
    NO_MATCH_THRESHOLD = .65
   
    if not results or results[0][0] < NO_MATCH_THRESHOLD:
        return jsonify({
            "status": "no_match",
            "message": "No relevant information found."
        }), 200


    
    context = ""

    for _, chunk, filename in results:
        context += f"""
        Source: {filename}
        Chunk: {chunk.chunk_index}

        {chunk.content}
        ---
        """


    prompt = f"""
        You are a helpful assistant.
        Answer the user's question using only the provided context.
        If the context does not contain the answer, say you do not know.

        Context:
        {context}

        Question:
        {question}
    """


    
    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt
        )
        answer = response.text

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }, 500
    
    citations = []

    for _, chunk, filename in results:
        citations.append({
            "filename": filename,
            "chunk_index": chunk.chunk_index
        })


    return jsonify({
        "status": "success",
        "answer": answer,
        "citations": citations
    })


@app.route("/")
def home():
    return render_template("index.html")        


if __name__ == "__main__":
    app.run(debug=True)