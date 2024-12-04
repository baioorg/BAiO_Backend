import json
from baio.src.agents import go_nl_agent
from langchain.chat_models import ChatOpenAI
import os

with open('chat/baio_container/baio_agents.json', 'r') as f:
    functions_config = json.load(f)


print(functions_config["tools"][0])

