from azure.cognitiveservices.vision.contentmoderator import ContentModeratorClient
from msrest.authentication import CognitiveServicesCredentials
from io import StringIO
import os
from dotenv import load_dotenv, find_dotenv
from openai import AzureOpenAI
from typing import Dict

class Response:
    """
    A class to handle user queries by moderating the text and generating responses
    using Azure Cognitive Services and OpenAI.

    Attributes:
        user_query (str): The query provided by the user.
    """

    def __init__(self, query: str) -> None:
        """
        Initialize the Response class with a user query and load environment variables.

        Args:
            query (str): The user's query.
        """
        self.user_query: str = query
        env_path = find_dotenv("config/.env")
        load_dotenv(env_path)
        self.moderator_setup

    @property
    def moderator_setup(self) -> Dict:
        """
        Set up the content moderator by loading the necessary environment variables
        and handling the user message.

        Returns:
            Dict: The moderation result as a dictionary.
        """
        self.moderator_endpoint: str = os.getenv("CONTENT_MODERATOR_ENDPOINT")
        self.moderator_api_key: str = os.getenv("CONTENT_MODERATOR_KEY")
        moderator_obj: Dict = self.handle_user_message()
        return moderator_obj

    def moderate_text(self, text: str) -> Dict:
        """
        Moderate the provided text using Azure Content Moderator.

        Args:
            text (str): The text to be moderated.

        Returns:
            Dict: The moderation response as a dictionary.
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

    def handle_user_message(self) -> Dict:
        """
        Handle the user message by moderating the text and returning the result.

        Returns:
            Dict: The moderation result as a dictionary.
        """
        moderation_result: Dict = self.moderate_text(self.user_query)
        return moderation_result

    @property
    def chat_completion_setup(self) -> str:
        """
        Set up the chat completion by loading the necessary environment variables
        and generating a response using OpenAI.

        Returns:
            str: The final response from the chat completion.
        """
        self.service_endpoint: str = os.getenv("AZURE_ENDPOINT")
        self.api_key: str = os.getenv("AZURE_RESOURCE_KEY")
        self.deployment: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.chat_completion_client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        )
        final_response: str = self.chat_completion()
        return final_response

    def chat_completion(self) -> str:
        """
        Generate a chat completion response using OpenAI.

        Returns:
            str: The content of the completion response.
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
                        "role_information": '''You are an AI assistant designed to answer questions based solely on the provided dataset. Your responses must be accurate and strictly derived from the dataset. If a user asks a question not covered by the dataset, respond in a varied manner without referencing the dataset. Use variations such as: "I can't answer that. Please ask another question.", "Sorry, I can't help with that. Please ask something else.", "I don't have information on that. Could you ask a different question?"''',
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
        Clean up the object.
        """
        pass
