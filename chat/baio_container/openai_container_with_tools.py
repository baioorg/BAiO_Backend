import openai
import threading
import json
from django.conf import settings
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from baio.src.agents import aniseed_agent, baio_agent, csv_chatter_agent, go_nl_agent

# Load the tools configuration
with open('chat/baio_container/baio_agents.json', 'r') as f:
    tools_config = json.load(f)

class StreamingCallbackHandler(BaseCallbackHandler):
    def __init__(self, queue):
        self.queue = queue

    def on_llm_new_token(self, token: str, **kwargs):
        self.queue.put(token)

class Message_Container(threading.Thread):
    def __init__(self, messages, queue, apikey, model):
        threading.Thread.__init__(self)
        self.messages = messages
        self.queue = queue
        self.apikey = apikey
        self.model = model
        self.tools = tools_config["tools"]
        
        # Initialize LangChain ChatOpenAI
        self.llm = ChatOpenAI(
            model_name=self.model,
            openai_api_key=self.apikey.key,
            streaming=True,
            callbacks=[StreamingCallbackHandler(self.queue)]
        )

    def _call_function(self, function_name: str, arguments: dict):
        """Execute the appropriate function based on the model's choice"""
        if function_name == "aniseed_agent":
            return aniseed_agent(arguments["query"], self.llm)
        elif function_name == "baio_agent":
            return baio_agent(arguments["query"], self.llm)
        elif function_name == "csv_chatter_agent":
            return csv_chatter_agent(arguments["query"], arguments["file_name"], self.llm)
        elif function_name == "nl_to_go_agent":
            return go_nl_agent(arguments["query"], self.llm)
        return None

    def run(self):
        try:
            openai.api_key = self.apikey.key

            stream = openai.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.tools,
                tool_choice="auto",
                max_tokens=1000,
                stream=True
            )

            function_name = None
            function_args = ""

            for chunk in stream:
                if hasattr(chunk.choices[0].delta, 'tool_calls'):
                    tool_calls = chunk.choices[0].delta.tool_calls
                    if tool_calls:
                        for tool_call in tool_calls:
                            if hasattr(tool_call, 'function'):
                                if hasattr(tool_call.function, 'name'):
                                    function_name = tool_call.function.name
                                if hasattr(tool_call.function, 'arguments'):
                                    function_args += tool_call.function.arguments

                elif hasattr(chunk.choices[0].delta, 'content'):
                    content = chunk.choices[0].delta.content
                    if content:
                        self.queue.put(content)

                # If we've collected a complete function call, execute it
                if function_name and function_args:
                    try:
                        args = json.loads(function_args)
                        function_response = self._call_function(function_name, args)
                        
                        # Add the function response to messages and continue the conversation
                        self.messages.append({
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [{
                                "id": "call_1",
                                "type": "function",
                                "function": {
                                    "name": function_name,
                                    "arguments": function_args
                                }
                            }]
                        })
                        self.messages.append({
                            "role": "tool",
                            "tool_call_id": "call_1",
                            "content": str(function_response)
                        })

                        # Continue the conversation with the function result
                        continuation = openai.chat.completions.create(
                            model=self.model,
                            messages=self.messages,
                            tools=self.tools,
                            tool_choice="auto",
                            max_tokens=1000,
                            stream=True
                        )

                        for cont_chunk in continuation:
                            if hasattr(cont_chunk.choices[0].delta, 'content'):
                                content = cont_chunk.choices[0].delta.content
                                if content:
                                    self.queue.put(content)

                    except Exception as e:
                        self.queue.put(f"\nError executing function: {str(e)}\n")
                    
                    # Reset function tracking
                    function_name = None
                    function_args = ""

            self.queue.put("DONE")

        except Exception as e:
            print(f"Error: {str(e)}")
            self.queue.put("DONE")
