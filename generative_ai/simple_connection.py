import os

from dotenv import load_dotenv
from openai import AzureOpenAI

client = AzureOpenAI(
        azure_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"], 
        api_key=os.environ['AZURE_OPENAI_API_KEY'],  
        api_version = "*REDACTED*"
    )
