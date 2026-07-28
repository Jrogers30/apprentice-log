#The Apprentice LOG!

A web app where you upload your own documents code, notes or anything text based and ask questions with cited from the documents. It finds the most relevant parts of your documents, generates an answer, and shows exactly which file and chunk the answer came from.

Live: https://apprentice-log.onrender.com

#What it does
Create an account and log in
Upload .py, .txt, or .md files
Ask a question, get an answer sourced from your own documents, with citations
If nothing relevant is found, it says so instead of guessing
How it works
Chunking —> code files are split by function/class; text files are split by paragraph.
Embedding —> each chunk is turned into a vector using Gemini's embedding model.
Retrieval —> your question is embedded too, then compared to your chunks by similarity. The closest matches are pulled.
Answering —> if the best match is confident enough, those chunks are sent to Gemini to generate an answer, using only that context. Otherwise, it says it doesn't know.
Retrieval evaluation

Instead of guessing a similarity threshold, I measured one. I ran 13 test questions —> 8 relevant, 5 unrelated —> against the retrieval function:

Unrelated questions scored 0.60 or lower
Relevant questions scored 0.71 or higher

so I set the threshold at 0.65 right in the middle, with room for error on both sides which is pretty good.

#Security
Passwords are hashed with bcrypt
Sessions are handled by Flask-Login
Each user can only see their own documents
API keys and secrets are kept out of the codebase (not committed to Git and yes if anyone is reading this do not give your API_KEYS to any LLM please:)  )



#Tech stack
Backend: Python, Flask, SQLAlchemy, bcrypt
Database: PostgreSQL (production), SQLite (local)
AI: Google Gemini, embeddings + generation
Frontend: HTML, CSS, JavaScript
Deployment: Render
Running it locally
bash
git clone [your repo URL]
cd apprentice_log
pip install -r requirements.txt

Add a .env file:

SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-key
bash
python app.py

Then open http://127.0.0.1:5000/.

