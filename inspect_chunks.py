from app import app, engine, Session, Document, Chunk

with app.app_context():

    with Session(engine) as session:

        doc = session.query(Document).filter_by(
            filename="design_docs.md"
        ).first()

        if not doc:
            print("design_docs.md not found.")
            exit()

        print(f"Document ID: {doc.id}\n")

        chunks = (
            session.query(Chunk)
            .filter_by(document_id=doc.id)
            .order_by(Chunk.chunk_index)
            .all()
        )

        print("Total Chunks:", len(chunks))
        print()

        indexes = [8, 17, 25]

    for idx in indexes:
        found = False

        for chunk in chunks:
            if chunk.chunk_index == idx:
                print("=" * 60)
                print(f"Chunk {idx}")
                print(chunk.content)
                found = True
                break

        if not found:
            print(f"Chunk {idx} does not exist.")