from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")

def analyze_expenses(expenses):

    prompt = f"""
    You are a financial advisor.

    Analyze these expenses:

    {expenses}

    Give:

    1. Spending summary
    2. Highest spending category
    3. Savings suggestions
    4. Interesting observations

    Keep it under 200 words.
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content