import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def analyze_expenses(expenses):

    prompt = f"""
    You are a financial advisor.

    Analyze the following expenses:

    {expenses}

    Give:

    1. Spending Summary
    2. Highest Spending Category
    3. Saving Suggestions
    4. Interesting Insights

    Keep the response under 200 words.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

def ask_ai(question, expenses):

    prompt = f"""
    You are an AI Financial Assistant.

    Here are the user's expenses:

    {expenses}

    The user asked:
    {question}

    Answer based on the expense data.
    If the user asks for advice, provide useful financial suggestions.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text
    return response.text
def ask_ai(question, expenses):

    prompt = f"""
You are an AI Financial Assistant.

Here are the user's expenses:

{expenses}

User Question:

{question}

Answer only using the expense data.
If the answer requires advice, provide practical financial suggestions.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text