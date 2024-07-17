from azure.cognitiveservices.vision.contentmoderator import ContentModeratorClient
from msrest.authentication import CognitiveServicesCredentials
from io import StringIO
import os
from dotenv import load_dotenv, find_dotenv
import os
from openai import AzureOpenAI
from dotenv import load_dotenv, find_dotenv
import re

class Response:
    def __init__(self,query):
        self.user_query=query
        env_path = find_dotenv("config/.env")
        load_dotenv(env_path)
        self.moderator_setup()


    def moderator_setup(self):
        self.moderator_endpoint = os.getenv("CONTENT_MODERATOR_ENDPOINT")
        self.moderator_api_key = os.getenv("CONTENT_MODERATOR_KEY")   
        self.handle_user_message() 

    def moderate_text(self,text):
        client = ContentModeratorClient(self.moderator_endpoint, CognitiveServicesCredentials(self.moderator_api_key))
        response = client.text_moderation.screen_text(
                text_content=StringIO(text),
                language="eng",
                text_content_type="text/plain",
                autocorrect=True,
                classify=True
    )
        return response.as_dict()

    def handle_user_message(self):
        moderation_result = self.moderate_text(self.user_query)
        if moderation_result.get('classification').get("category3").get("score") > 0.3 or moderation_result.get('classification').get("category2").get("score") > 0.3 or moderation_result.get('classification').get("category1").get("score") > 0.3 or moderation_result.get('classification').get('review_recommended') == True:
            print("Response: I can't answer questions like that.Please ask another question.")
        else:
            self.chat_completion_setup()
        
    def chat_completion_setup(self):
        self.service_endpoint = os.getenv("AZURE_ENDPOINT")
        self.api_key = os.getenv("AZURE_RESOURCE_KEY")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.chat_completion_client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            )
        self.chat_completion()
    
    def chat_completion(self):      
        completion = self.chat_completion_client.chat.completions.create(
            model=self.deployment,
            messages= [   
            {
            "role": "user",
            "content": self.user_query
            }],
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
        print("Response: ",re.sub(r'\[doc\d+\]', '', completion.choices[0].message.content))
    

