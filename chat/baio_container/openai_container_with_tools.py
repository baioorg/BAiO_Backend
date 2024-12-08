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

# Load the tools configuration from JSON file that defines available function calls for the OpenAI API
with open('chat/baio_container/baio_agents.json', 'r') as f:
    functions_config = json.load(f)

class StreamingCallbackHandler(BaseCallbackHandler):
    """Handles streaming of tokens from LangChain's LLM responses"""
    def __init__(self, queue):
        self.queue = queue

    def on_llm_new_token(self, token: str, **kwargs):
        self.queue.put(token)

class Message_Container(threading.Thread):
    """
    Manages OpenAI chat completions with function calling capabilities.
    Runs as a separate thread to handle async streaming responses.
    """
    def __init__(self, messages, queue, apikey, model, conversation_id, url):
        threading.Thread.__init__(self)
        self.messages = messages
        self.queue = queue
        self.apikey = apikey
        self.model = model
        self.tools = functions_config["tools"]
        self.conversation_id = conversation_id
        self.url = url
        # Possible security risk?
        os.environ['OPENAI_API_KEY'] = apikey
        self.llm = ChatOpenAI(model=self.model, temperature=0, api_key=apikey, base_url=url)
        self.embedding = OpenAIEmbeddings(api_key=apikey, base_url=url)
    
    def aniseed_function(self, query, message_id):
        """Processes ANISEED database queries and creates CSV files with results"""
        csv_files = aniseed_agent(query, self.llm)
        # Store CSV file references in database and update available tools
        for csv_file in csv_files:
            CSVFile.objects.create(
                message=Message.objects.get(id=message_id),
                file_name=csv_file.split("/")[-1],
                file_path=csv_file
            )
            # Add new CSV file to available options for csv_chatter_agent
            self.tools[2]["function"]["parameters"]["properties"]["file_name"]["enum"].append(csv_file.split("/")[-1])

        return f"CSV Files created:[\n {', '.join(csv_files)}]"
    
    def baio_function(self, query):
        """Processes general bioinformatics queries using vector embeddings"""
        return str(baio_agent(query, self.llm, self.embedding))
    
    def csv_chatter_function(self, query, file_names):
        """Enables natural language interaction with CSV files"""
        file_paths = CSVFile.objects.filter(file_name__in=file_names,
                                            message__conversation_id=self.conversation_id
                                            ).values_list('file_path', flat=True)
        return str(csv_chatter_agent(query, file_paths, self.llm))
    
    def go_nl_function(self, query):
        """Processes Gene Ontology related natural language queries"""
        return str(go_nl_agent(query, self.llm))

    def get_csv_files_in_conversation(self, conversation_id):
        """Retrieves all CSV files associated with a specific conversation"""
        conversation = Conversation.objects.get(id=conversation_id)
        messages = Message.objects.filter(conversation=conversation)
        csv_files = CSVFile.objects.filter(message__in=messages)
        return [csv_file.file_name for csv_file in csv_files]
    
    def _call_function(self, function_name, args):
        """Routes function calls to appropriate handlers based on function name"""
        print(f"Calling function: {function_name} with args: {args}")
        if function_name == "aniseed_agent":
            return self.aniseed_function(args["query"], args["message_id"])
        if function_name == "baio_agent":
            return self.baio_function(args["query"])
        if function_name == "csv_chatter_agent":
            return self.csv_chatter_function(args["query"], args["file_name"])
        if function_name == "go_nl_agent":
            return self.go_nl_function(args["query"])
        print(f"Warning: Unknown function {function_name}")
        return f"Unknown function {function_name}"

    def run(self):
        """
        Main execution loop that handles:
        1. OpenAI API streaming responses
        2. Function calling
        3. Message history management
        4. Error handling
        
        Allows up to 5 API calls per run to handle complex multi-step interactions
        where the model needs to call multiple functions sequentially.
        """
        try:
            openai.api_key = self.apikey
            openai.base_url = self.url

            # Update available CSV files for the current conversation

            self.tools[2]["function"]["parameters"]["properties"]["file_names"]["items"]["enum"] = self.get_csv_files_in_conversation(self.conversation_id)
            
            api_calls = 0
            while api_calls < 5:
                api_calls += 1
                # Stream response from OpenAI API
                response = openai.chat.completions.create(
                    model = self.model,
                    messages = self.messages,
                    max_tokens=1000,
                    tools=self.tools,
                    stream=True,
                    temperature=0.3
                )

                # Initialize collectors for response processing
                assistant_response = ""
                called_functions = []

                print("Processing response stream...")
                # Process streaming response chunks
                for chunk in response:
                    delta = chunk.choices[0].delta
                    if delta.tool_calls is not None:
                        # Handle function call information in the response
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

                # Execute any functions called by the model
                function_responses = []
                for function in called_functions:
                    function_name = function["name"]
                    function_args = function["args"]

                    try:
                        args = json.loads(function_args)
                        # Add message_id for database operations
                        args['message_id'] = Message.objects.filter(conversation_id=self.conversation_id).last().id
                        function_response = self._call_function(function_name, args)

                        # Update message history with function call
                        self.messages.append({
                            "role": "assistant",
                            "content": None,
                            "function_call": {
                                "name": function_name,
                                "arguments": function_args
                            }
                        })
                        # Add function response to message history
                        self.messages.append({
                            "role": "function",
                            "name": function_name,
                            "content": function_response
                        })

                        function_responses.append(f"{{name:{function_name}, response:{function_response}}}")

                    except Exception as e:
                        print(f"Error executing function: {str(e)}")
                        error_message = f"Error executing function{function_name} with args {str(function_args)}. Received error {str(e)}\n. Please rewrite your query and try again."
                        self.messages.append({
                            "role": "function",
                            "name": function_name,
                            "content": error_message})
                        function_responses.append(error_message)
                
                # Break if no functions were called, otherwise continue the conversation
                if(len(called_functions) == 0):
                    break
                else:
                    self.queue.put(f"function_responses:{str(function_responses)}")

            self.queue.put("DONE")

        except Exception as e:
            print(f"Error in run method: {str(e)}")
            self.queue.put(f"Error: {str(e)}")
            self.queue.put("DONE")
