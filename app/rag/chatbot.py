from openai import OpenAI

from config import get_config


config = get_config()


class OpenAIChatbot:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def ask_question(self, question: str, context: str) -> str:
        client = OpenAI(api_key=config.OPENAI_API_KEY)

        completion = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": f"{question}\n\nHere is the context:\n{context}",
                },
            ],
        )
        return completion.choices[0].message
