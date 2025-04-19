import openai

from env import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)