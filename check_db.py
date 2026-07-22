from app import Session, engine, Document

with Session(engine) as session:
    for d in session.query(Document).all():
        print(d.id, d.user_id, d.filename, len(d.content))