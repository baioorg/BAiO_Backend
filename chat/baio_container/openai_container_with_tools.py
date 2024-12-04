import openai
import threading
import json
from django.conf import settings
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.callbacks.base import BaseCallbackHandler
from baio.src.agents import aniseed_agent, baio_agent, csv_chatter_agent, go_nl_agent
from chat.models import CSVFile, Message, Conversation

import os

# Load the tools configuration
with open('chat/baio_container/baio_agents.json', 'r') as f:
    functions_config = json.load(f)

class StreamingCallbackHandler(BaseCallbackHandler):
    def __init__(self, queue):
        self.queue = queue

    def on_llm_new_token(self, token: str, **kwargs):
        self.queue.put(token)

class Message_Container(threading.Thread):
    def __init__(self, messages, queue, apikey, model, conversation_id):
        threading.Thread.__init__(self)
        self.messages = messages
        self.queue = queue
        self.apikey = apikey
        self.model = model
        self.tools = functions_config["tools"]
        self.conversation_id = conversation_id
        #Possible security risk?
        os.environ['OPENAI_API_KEY'] = apikey
        self.llm = ChatOpenAI(model=self.model, temperature=0, api_key=apikey)
        self.embedding = OpenAIEmbeddings(api_key=apikey)
        print("test init end")
    
    def aniseed_function(self, query, message_id):
        csv_files = aniseed_agent(query, self.llm)
        for csv_file in csv_files:
            CSVFile.objects.create(
                message=Message.objects.get(id=message_id),
                file_name=csv_file.split("/")[-1],
                file_path=csv_file
            )
            self.tools[2]["function"]["parameters"]["properties"]["file_name"]["enum"].append(csv_file.split("/")[-1])

        return f"CSV Files created:[\n {', '.join(csv_files)}]"
    
    def baio_function(self, query):
        return str(baio_agent(query, self.llm, self.embedding))
    
    def csv_chatter_function(self, query, file_name):
        file_path = CSVFile.objects.get(file_name=file_name).file_path
        return str(csv_chatter_agent(query, [file_path], self.llm))
    
    def go_nl_function(self, query):
        return str(go_nl_agent(query, self.llm))

    def get_csv_files_in_conversation(self, conversation_id):
        conversation = Conversation.objects.get(id=conversation_id)
        messages = Message.objects.filter(conversation=conversation)
        csv_files = CSVFile.objects.filter(message__in=messages)

        return [csv_file.file_name for csv_file in csv_files]
    
    def _call_function(self, function_name, args):
        print(f"Calling function: {function_name} with args: {args}")
        if function_name == "aniseed_agent":
            return self.aniseed_function(args["query"], args["message_id"])
        if function_name == "baio_agent":
            return self.baio_function(args["query"])
        if function_name == "csv_chatter_function":
            return self.csv_chatter_function(args["query"], args["file_name"])
        if function_name == "go_nl_agent":
            return self.go_nl_function(args["query"])
        print(f"Warning: Unknown function {function_name}")
        return f"Unknown function {function_name}"

    def run(self):
        try:
            print("test run start")
            openai.api_key = self.apikey

            self.tools[2]["function"]["parameters"]["properties"]["file_name"]["enum"] = self.get_csv_files_in_conversation(self.conversation_id)
            
            api_calls = 0
            while api_calls<5:
                api_calls+=1
                # Make the API call with streaming
                response = openai.chat.completions.create(
                    model = self.model,
                    messages = self.messages,
                    max_tokens=1000,
                    tools=self.tools,
                    stream=True
                )

                # Initialize variables to collect the assistant's response
                assistant_response = ""
                called_functions = []

                print("Processing response stream...")
                for chunk in response:
                    delta = chunk.choices[0].delta
                    if delta.tool_calls is not None:
                        # Collect tool_calls data
                        index = delta.tool_calls[0].index
                        if delta.tool_calls[0].function.name is not None:
                            called_functions.append({"name":delta.tool_calls[0].function.name, "args":""})
                            if(index == 0):
                                self.queue.put(f"called_functions:[{{name:{delta.tool_calls[0].function.name}, args:")
                            else:
                                self.queue.put(f"}},{{name:{delta.tool_calls[0].function.name}, args:")
                        if delta.tool_calls[0].function.arguments is not None:
                            called_functions[index]["args"] += delta.tool_calls[0].function.arguments
                            self.queue.put(delta.tool_calls[0].function.arguments)
                    elif delta.content is not None:
                        content = delta.content
                        if content:
                            self.queue.put(content)
                            assistant_response += content
                
                if(len(called_functions) > 0):
                    self.queue.put("}]")
                            
                print(f"Assistant response: {assistant_response}")
                print(f"Called functions: {called_functions}")

                # If a function call was made, execute the function
                for function in called_functions:
                    function_name = function["name"]
                    function_args = function["args"]

                    try:
                        args = json.loads(function_args)
                        # Add the message_id to args if needed
                        args['message_id'] = Message.objects.filter(conversation_id=self.conversation_id).last().id
                        function_response = self._call_function(function_name, args)

                        # Add the assistant's message with function call
                        self.messages.append({
                            "role": "assistant",
                            "content": None,
                            "function_call": {
                                "name": function_name,
                                "arguments": function_args
                            }
                        })
                        # Add the function's response
                        self.messages.append({
                            "role": "function",
                            "name": function_name,
                            "content": function_response
                        })

                    except Exception as e:
                        print(f"Error executing function: {str(e)}")
                        self.messages.append({
                            "role": "function",
                            "name": function_name,
                            "content": f"\nError executing function{function_name} with args {str(function_args)}. Received error {str(e)}\n. Please rewrite your query and try again."})
                    
                
                # Response has finished
                if(len(called_functions) == 0):
                    break

            self.queue.put("DONE")

        except Exception as e:
            print(f"Error in run method: {str(e)}")
            self.queue.put(f"Error: {str(e)}")
            self.queue.put("DONE")
