from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    LLM_MODEL="openai:gpt-4o"

    CHUNK_SIZE=500
    CHUNK_OVERLAP = 50

    DEFAULT_URLS = [
        "https://lilianweng.github.io/posts/2023-06-23-agent/",
        "https://lilianweng.github.io/posts/2024-04-12-diffusion-video/"
    ]

    @classmethod
    def get_llm(cls):
        os.environ["OPENAI_API_KEY"]  = cls.OPENAI_API_KEY
        return init_chat_model(model=cls.LLM_MODEL)


