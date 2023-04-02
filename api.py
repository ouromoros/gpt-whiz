import requests
from typing import List, Optional, Dict, Any

class Message:
    def __init__(self, role: str, content: str, name: Optional[str] = None):
        self.role = role
        self.content = content
        self.name = name
    
    def to_dict(self):
        if self.name is not None:
            return {
                "role": self.role,
                "name": self.name,
                "content": self.content,
            }
        else:
            return {
                "role": self.role,
                "content": self.content,
            }

class ChatCompletion:
    def __init__(self, data: Dict[str, Any]):
        self.id = data['id']
        self.object = data['object']
        self.created = data['created']
        self.model = data['model']
        self.usage = data['usage']
        self.choices = data['choices']

def chat_completion(api_key: str, model: str, messages: List[Message], temperature: Optional[float] = None, n: Optional[int] = None) -> ChatCompletion:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    data = {
        "model": model,
        "messages": [message.to_dict() if isinstance(message, Message) else message for message in messages],
        # "temperature": temperature,
        # "n": n,
    }
    # print(data)
    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to complete chat: {response.status_code} {response.reason}")
    response_data = response.json()
    return ChatCompletion(response_data)

class OpenAIChatModel:
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model

    def chat_complete(self, prompt_messages: List[Message], stop: List[str] = []) -> Message:
        response = chat_completion(self.api_key, self.model, prompt_messages)
        return Message(**response.choices[0]['message'])

if __name__ == "__main__":
    proxy = "http://127.0.0.1:9999"
    import os
    os.environ["http_proxy"] = proxy
    os.environ["https_proxy"] = proxy
    api = OpenAIChatModel("sk-xxxxxxxxx")
    msg = api.chat_complete([
        Message("user", "hello!"),
    ])
    print(msg.__dict__)