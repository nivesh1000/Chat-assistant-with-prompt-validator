from azure.cognitiveservices.vision.contentmoderator import ContentModeratorClient
from msrest.authentication import CognitiveServicesCredentials
from io import StringIO
import os
from dotenv import load_dotenv, find_dotenv
from openai import AzureOpenAI
from pydantic import BaseModel, ValidationError


class Settings(BaseModel):
    CONTENT_MODERATOR_ENDPOINT: str
    CONTENT_MODERATOR_KEY: str
    AZURE_ENDPOINT: str
    AZURE_RESOURCE_KEY: str
    AZURE_OPENAI_DEPLOYMENT_NAME: str
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_ENDPOINT: str


class Response:
    def __init__(self, query: str) -> None:
        """
        Initialize the Response class with a user query and set up environment
        variables.

        Args:
            query (str): The user query.
        """
        self.user_query: str = query
        env_path = find_dotenv("config/.env")
        load_dotenv(env_path)
        self.settings: Settings = self.load_settings()
        self.moderator_setup

    def load_settings(self) -> Settings:
        """
        Load and validate settings from environment variables.

        Returns:
            Settings: Validated settings object.
        """
        try:
            settings = Settings(
                CONTENT_MODERATOR_ENDPOINT=os.getenv("CONTENT_MODERATOR_ENDPOINT"),
                CONTENT_MODERATOR_KEY=os.getenv("CONTENT_MODERATOR_KEY"),
                AZURE_ENDPOINT=os.getenv("AZURE_ENDPOINT"),
                AZURE_RESOURCE_KEY=os.getenv("AZURE_RESOURCE_KEY"),
                AZURE_OPENAI_DEPLOYMENT_NAME=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                AZURE_OPENAI_API_KEY=os.getenv("AZURE_OPENAI_API_KEY"),
                AZURE_OPENAI_ENDPOINT=os.getenv("AZURE_OPENAI_ENDPOINT"),
            )
            return settings
        except ValidationError as e:
            print("Environment variables validation error:", e)
            raise

    @property
    def moderator_setup(self) -> dict:
        """
        Set up the content moderator client using environment variables.

        Returns:
            dict: The moderation result as a dictionary.
        """
        self.moderator_endpoint: str = self.settings.CONTENT_MODERATOR_ENDPOINT
        self.moderator_api_key: str = self.settings.CONTENT_MODERATOR_KEY
        moderator_obj: dict = self.handle_user_message()
        return moderator_obj

    def moderate_text(self, text: str) -> dict:
        """
        Moderate the given text using the Azure Content Moderator.

        Args:
            text (str): The text to be moderated.

        Returns:
            dict: The moderation response as a dictionary.
        """
        client = ContentModeratorClient(
            self.moderator_endpoint,
            CognitiveServicesCredentials(self.moderator_api_key)
        )
        response = client.text_moderation.screen_text(
            text_content=StringIO(text),
            language="eng",
            text_content_type="text/plain",
            autocorrect=True,
            classify=True
        )
        return response.as_dict()

    def handle_user_message(self) -> dict:
        """
        Handle the user message by moderating it.

        Returns:
            dict: The moderation result as a dictionary.
        """
        moderation_result: dict = self.moderate_text(self.user_query)
        return moderation_result

    @property
    def chat_completion_setup(self) -> str:
        """
        Set up the chat completion client using environment variables.

        Returns:
            str: The final chat completion response.
        """
        self.service_endpoint: str = self.settings.AZURE_ENDPOINT
        self.api_key: str = self.settings.AZURE_RESOURCE_KEY
        self.deployment: str = self.settings.AZURE_OPENAI_DEPLOYMENT_NAME
        self.chat_completion_client = AzureOpenAI(
            api_key=self.settings.AZURE_OPENAI_API_KEY,
            api_version="2024-02-01",
            azure_endpoint=self.settings.AZURE_OPENAI_ENDPOINT,
        )
        final_response: str = self.chat_completion()
        return final_response

    def chat_completion(self) -> str:
        """
        Generate a chat completion based on the user query.

        Returns:
            str: The chat completion response.
        """
        completion = self.chat_completion_client.chat.completions.create(
            model=self.deployment,
            messages=[
                {
                    "role": "user",
                    "content": self.user_query
                }
            ],
            max_tokens=800,
            temperature=0,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            stream=False,
            extra_body={
                "data_sources": [{
                    "type": "azure_search",
                    "parameters": {
                        "endpoint": f"{self.service_endpoint}",
                        "index_name": "petofy-webdata-index",
                        "semantic_configuration": "default",
                        "query_type": "simple",
                        "fields_mapping": {},
                        "in_scope": True,
                        "role_information": '''You are an AI assistant designed
                        to answer questions based solely on the provided dataset.
                        Your responses must be accurate and strictly derived from
                        the dataset. If a user asks a question not covered by the
                        dataset, respond in a varied manner without referencing
                        the dataset. Use variations such as: "I can't answer that.
                        Please ask another question.", "Sorry, I can't help with
                        that. Please ask something else.", "I don't have information
                        on that. Could you ask a different question?"''',
                        "filter": None,
                        "strictness": 3,
                        "top_n_documents": 5,
                        "authentication": {
                            "type": "api_key",
                            "key": f"{self.api_key}"
                        }
                    }
                }]
            }
        )
        return completion.choices[0].message.content

    def __del__(self) -> None:
        """
        Destructor for the Response class.
        """
        pass
