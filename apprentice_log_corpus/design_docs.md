# Apprentice Log -- Revised Design Document

## SCHEMA

### users

-   id
-   email
-   password_hash

### documents

-   id
-   user_id (FK → users.id)
-   filename
-   content

### chunks

-   id
-   document_id (FK → documents.id)
-   chunk_index
-   content
-   embedding

------------------------------------------------------------------------

# ROUTES

## POST /register

**Takes** - email - password

**Process** - Creates a new user. - Hashes the password before storing
it.

**Success Return**

``` json
{"status":"success","message":"Account created."}
```

**Failure Return**

``` json
{"status":"error","message":"Email already exists."}
```

------------------------------------------------------------------------

## POST /login

**Takes** - email - password

**Process** - Verifies credentials. - Creates a secure authenticated
session (signed cookie).

**Success Return**

``` json
{"status":"success","message":"Logged in successfully."}
```

**Failure Return**

``` json
{"status":"error","message":"Invalid email or password."}
```

------------------------------------------------------------------------

## POST /logout

**Process** - Removes the authenticated session. - Logs the user out.

**Return**

``` json
{"status":"success","message":"Logged out successfully."}
```

------------------------------------------------------------------------

## POST /upload

**Takes** - Uploaded document

**Process** 1. Uses the authenticated session to identify the user. 2.
Stores the document and filename. 3. Splits the document into chunks. 4.
Generates an embedding for each chunk. 5. Stores each chunk and its
embedding.

**Success Return**

``` json
{"document_id":12,"chunk_count":38,"status":"success"}
```

**Failure Return**

``` json
{"status":"error","message":"Authentication required."}
```

------------------------------------------------------------------------

## POST /ask

**Takes** - User question

**Process** 1. Uses the authenticated session. 2. Embeds the user's
question. 3. Compares it with stored chunk embeddings for only that
user's documents. 4. Retrieves the most relevant chunks. 5. Generates an
answer. 6. Returns citations.

**Success Return**

``` json
{
  "answer":"Your answer goes here.",
  "citations":[
    {"filename":"bug2_review.txt","chunk_index":4},
    {"filename":"dungeon_final.py","chunk_index":11}
  ]
}
```

**NO match Return**
``` json
{
    "status": "no_match",
    "message": "I couldn't find any relevant information in your uploaded documents to answer that question."
}
``` 


**Failure Return**

``` json
{"status":"error","message":"Authentication required."}
```

------------------------------------------------------------------------

# CHUNKING STRATEGY

### `.py`

Split on `def` / `class` boundaries.

**Why:** A function or class is a self-contained unit of meaning.
Cutting in the middle produces incomplete logic and loses context needed
for retrieval and citation.

### `.txt` / `.md`

Split on paragraph boundaries.

**Why:** A paragraph usually contains one complete thought. Keeping
paragraphs intact preserves context and avoids splitting an explanation
in half.

------------------------------------------------------------------------

# DESIGN DECISION

Apprentice Log answers retrospective questions about a user's previously
uploaded coding history and documents with citations. It is **not**
designed for live code review.

------------------------------------------------------------------------

# CORPUS

The current Apprentice Log corpus contains:

- bug1.py
- bug2.py
- bug3.py
- bug_1reason.txt
- bug_2reason.txt
- bug_3reason.txt
- design_docs.md

