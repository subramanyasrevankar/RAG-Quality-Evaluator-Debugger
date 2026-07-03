from google import genai
import os
import traceback
from dotenv import load_dotenv

load_dotenv()

# Debug API key
print("Gemini API Key Loaded:", os.getenv("GEMINI_API_KEY") is not None)

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_answer(question: str, chunks: list) -> str:
    """
    Generates an answer using Gemini based only on retrieved chunks.
    """

    context = "\n\n".join(
        [f"Chunk {i+1}:\n{chunk}" for i, chunk in enumerate(chunks)]
    )

    prompt = f"""
You are a precise question-answering assistant.

Answer the question using ONLY the context provided below.

Do not use any outside knowledge.

If the answer is not found in the context, say exactly:

"I don't know based on the provided document."

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""

    try:
        print("\n========== Calling Gemini ==========")

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        print("========== Gemini Success ==========\n")

        return response.text.strip()

    except Exception as e:
        print("\n========== GEMINI ERROR ==========")
        traceback.print_exc()
        print("==================================\n")
        return f"Error generating answer: {e}"


def check_faithfulness_with_llm(
    question: str,
    answer: str,
    chunks: list,
) -> dict:

    context = "\n\n".join(
        [f"Chunk {i+1}:\n{chunk}" for i, chunk in enumerate(chunks)]
    )

    prompt = f"""
You are a faithfulness evaluator for Retrieval-Augmented Generation (RAG).

Given the CONTEXT, QUESTION, and ANSWER below, evaluate how faithful the answer is.

Faithfulness means:
- Every factual claim in the answer must be supported by the context.
- If the answer contains information not present in the context, it is hallucinated.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
{answer}

Respond EXACTLY in this format:

SCORE: <number between 0.0 and 1.0>
REASON: <one sentence>
HALLUCINATED: <yes or no>
"""

    try:

        print("\n========== Calling Gemini Judge ==========")

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        print("========== Judge Success ==========\n")

        return parse_faithfulness_response(response.text.strip())

    except Exception as e:

        print("\n========== JUDGE ERROR ==========")
        traceback.print_exc()
        print("=================================\n")

        return {
            "faithfulness_score": 0.0,
            "reason": str(e),
            "hallucinated": False,
        }


def parse_faithfulness_response(response: str) -> dict:

    result = {
        "faithfulness_score": 0.5,
        "reason": "Could not parse response",
        "hallucinated": False,
    }

    lines = response.strip().split("\n")

    for line in lines:

        line = line.strip()

        if line.startswith("SCORE:"):
            try:
                score = float(line.replace("SCORE:", "").strip())
                score = max(0.0, min(1.0, score))
                result["faithfulness_score"] = round(score, 3)
            except:
                pass

        elif line.startswith("REASON:"):
            result["reason"] = line.replace("REASON:", "").strip()

        elif line.startswith("HALLUCINATED:"):
            result["hallucinated"] = (
                line.replace("HALLUCINATED:", "").strip().lower() == "yes"
            )

    return result