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
                max_tokens=100,
                stream=True
            )

            for chunk in stream:
                content = chunk.choices[0].delta.content if hasattr(chunk.choices[0].delta, 'content') else None
                if content:
                    self.queue.put(content)

        except Exception as e:
            self.queue.put(f"Exception: {str(e)}")
            self.queue.put(None)

