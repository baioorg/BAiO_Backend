import json

with open('chat/baio_container/baio_agents.json', 'r') as f:
    functions_config = json.load(f)


print(functions_config["tools"][0])

