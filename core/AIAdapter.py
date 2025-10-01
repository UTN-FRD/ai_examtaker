from google import genai
from google.genai import types

from settings.config import settings

class AIAdapter:
    def __init__(self, model: str):
        self.model = model
        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        self.generate_content_config = types.GenerateContentConfig(
            thinking_config = types.ThinkingConfig(
                thinking_budget=0,
            ),
        )

    def generate_content(self, user_prompt: str, system_prompt: str) -> types.Content:
        """ Generate content using the model """
        return self.client.models.generate_content(
            model=self.model,
            contents=[
                types.Content(
                    role="model",
                    parts=[
                        types.Part(text=system_prompt)
                    ]
                ),
                types.Content(
                    role="user",
                    parts=[
                        types.Part(text=user_prompt)
                    ]
                )
            ],
            config=self.generate_content_config,
        )

    def generate_structured_content(self, user_prompt: str, system_prompt: str, response_schema: type) -> types.GenerateContentResponse:
        """ Generate structured content using the model with a Pydantic schema """
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema,
            thinking_config=types.ThinkingConfig(
                thinking_budget=0,
            ),
        )

        return self.client.models.generate_content(
            model=self.model,
            contents=[
                types.Content(
                    role="model",
                    parts=[
                        types.Part(text=system_prompt)
                    ]
                ),
                types.Content(
                    role="user",
                    parts=[
                        types.Part(text=user_prompt)
                    ]
                )
            ],
            config=config,
        )