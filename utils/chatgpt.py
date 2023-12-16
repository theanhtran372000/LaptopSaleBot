import openai

class ChatGPTClient():
    def __init__(self, configs):
        self.client = openai.OpenAI()
        self.configs = configs
        
    def get_instance(self):
        return self.client
    
    def get_answer(self, history, stream=True):
        output = self.client.chat.completions.create(
            model=self.configs['openai']['model_name'],
            messages=[
                {
                    'role': m['role'],
                    'content': m['content']
                }
                for m in history
            ],
            stream=stream
        )
        
        if stream:
            return output # Return data stream
        else:
            return output.choices[0].message.content # Return answer
    
        