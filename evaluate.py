from app import retrieve




eval_set = [

    

    {
        "question": "How does the upload route work?",
        "expect_relevant": True,
        "expect_source": "design_docs.md"
    },

    {
        "question": "What does the logout route do?",
        "expect_relevant": True,
        "expect_source": "design_docs.md"
    },

    {
        "question": "How are Python files chunked?",
        "expect_relevant": True,
        "expect_source": "design_docs.md"
    },

    {
        "question": "How are markdown files chunked?",
        "expect_relevant": True,
        "expect_source": "design_docs.md"
    },

    {
        "question": "Why was the defend mechanic applying twice?",
        "expect_relevant": True,
        "expect_source": "bug_2reason.txt"
    },

    {
        "question": "What bug existed in bug1.py?",
        "expect_relevant": True,
        "expect_source": "bug1.py"
    },

    {
        "question": "What bug existed in bug2.py?",
        "expect_relevant": True,
        "expect_source": "bug2.py"
    },

    {
        "question": "What bug existed in bug3.py?",
        "expect_relevant": True,
        "expect_source": "bug3.py"
    },



    {
        "question": "What is the capital of France?",
        "expect_relevant": False,
        "expect_source": None
    },

    {
        "question": "Who won the Super Bowl?",
        "expect_relevant": False,
        "expect_source": None
    },

    {
        "question": "How do I bake cookies?",
        "expect_relevant": False,
        "expect_source": None
    },

    {
        "question": "What is photosynthesis?",
        "expect_relevant": False,
        "expect_source": None
    },

    {
        "question": "Who wrote Hamlet?",
        "expect_relevant": False,
        "expect_source": None
    }

]


print("=" * 100)
print("RETRIEVAL EVALUATION")
print("=" * 100)

results_data = []

for test in eval_set:

    question = test["question"]
    expected = test["expect_source"]

    results = retrieve(question, user_id=1, k=1)

    print("\n" + "-" * 100)
    print("Question:", question)

    if not results:
        print("No results returned.")
        results_data.append({
            "score": 0,
            "expected": test["expect_relevant"]
        })
        continue

    score, chunk, filename = results[0]

    results_data.append({
        "score": score,
        "expected": test["expect_relevant"]
    })

    print(f"Score: {score:.3f}")
    print("Retrieved :", filename)
    print("Expected  :", expected)

    if filename == expected:
        print("Correct Source: YES")
    else:
        print("Correct Source: NO")

    print("Preview:")
    print(chunk.content.split("\n")[0])



print("\n")
print("=" * 100)
print("THRESHOLD TEST")
print("=" * 100)

thresholds = [0.55, 0.60, 0.65, 0.70]

for threshold in thresholds:

    false_positive = 0
    false_negative = 0

    for item in results_data:

        prediction = item["score"] >= threshold

        if prediction and not item["expected"]:
            false_positive += 1

        if not prediction and item["expected"]:
            false_negative += 1

    print(f"\nThreshold: {threshold}")
    print(f"False Positives: {false_positive}")
    print(f"False Negatives: {false_negative}")