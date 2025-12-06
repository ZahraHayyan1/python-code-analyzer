import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("Anthropic API key not found. Set ANTHROPIC_API_KEY in .env")

llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", anthropic_api_key=api_key)

response = llm.invoke("what is the meaning of life?")
print(response)