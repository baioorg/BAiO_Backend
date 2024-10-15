import openai
import threading
from django.conf import settings

class Message_Container(threading.Thread):
    def __init__(self, messages, queue):
        threading.Thread.__init__(self)
        self.messages = messages
        self.queue = queue

    def run(self):

        try:

            openai.api_key = settings.OPENAI_API_KEY

            stream = openai.chat.completions.create(
                model = "gpt-4o-mini",
                messages = self.messages,
                max_tokens=100,
                stream=True
            )

            response = ""
            for chunk in stream:
                print(chunk)
                content = chunk.choices[0].delta.content if hasattr(chunk.choices[0].delta, 'content') else None
                if content:
                    response += content
                    self.queue.put(content)

        except Exception as e:
            self.queue.put(f"Exception: {str(e)}")
            self.queue.put(None)

