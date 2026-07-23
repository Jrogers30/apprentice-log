from app import chunk_python,chunk_paragraphs

with open("apprentice_log_corpus/bug2.py","r",encoding="utf-8") as f:
    text = f.read()

chunks = chunk_python(text)

for i,chunk in enumerate(chunks):
    firstLine = chunk.splitlines()[0]
    print(f"Chunk {i}: {firstLine}")


with open("apprentice_log_corpus/bug_2reason.txt", "r", encoding="utf-8") as f:
    text = f.read()

chunks = chunk_paragraphs(text)

print("Number of paragraphs:", len(chunks))

for i, chunk in enumerate(chunks):
    print(f"\nParagraph {i}:")
    print(chunk[:100])