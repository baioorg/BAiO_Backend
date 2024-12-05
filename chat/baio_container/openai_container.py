# Deprecated, use openai_container_with_tools instead

import openai
import threading
from django.conf import settings

class Message_Container(threading.Thread):
    def __init__(self, messages, queue, apikey, model):
        threading.Thread.__init__(self)
        self.messages = messages
        self.queue = queue
        self.apikey = apikey
        self.model = model

    def run(self):

        try:

            openai.api_key = self.apikey.key

            stream = openai.chat.completions.create(
                model = self.model,
                messages = self.messages,
                max_tokens=1000,
                stream=True
            )

            for chunk in stream:
                content = chunk.choices[0].delta.content if hasattr(chunk.choices[0].delta, 'content') else None
                if content:
                    self.queue.put(content)

            self.queue.put("DONE")

        except Exception as e:
            print(f"Error: {str(e)}")
            self.queue.put("DONE")

