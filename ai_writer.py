from groq import Groq


API_KEY = "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"


client = Groq(
    api_key=API_KEY
)


def rewrite_news(news):

    prompt = f"""
You are a professional football news editor for a football social media page.

Rewrite this football news into an original English post.

Rules:
- Write in English.
- Do NOT use "Here we go".
- Do NOT copy Fabrizio Romano style.
- Do NOT mention the source.
- Do NOT invent details.
- Keep it short and exciting.
- Use football emojis.
- Make it suitable for Instagram and Facebook.

News:
{news}
"""


    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )


    return response.choices[0].message.content