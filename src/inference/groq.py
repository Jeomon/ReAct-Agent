from src.inference.base import BaseInference
from src.message.base import AIMessage
from requests import post

class ChatGroq(BaseInference):
    def invoke(self, messages: list[dict],json=False):
        self.headers.update({'Authorization': f'Bearer {self.api_key}'})
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "https://api.groq.com/openai/v1/chat/completions"
        payload={
            "model": self.model,
            "messages": [message.to_dict() for message in messages],
            "temperature": temperature,
            "stream":False
        }
        if json:
            payload['response_format']={
                "type": "json_object"
            }
        try:
            response=post(url=url,json=payload,headers=headers)
            response.raise_for_status()
            json_obj=response.json()
            # print(json_obj)
            return AIMessage(json_obj['choices'][0]['message']['content'])
        except Exception as err:
            print(err)