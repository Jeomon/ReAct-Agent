from src.inference import BaseInference
from src.message import AIMessage,BaseMessage
from half_json.core import JSONFixer
from requests import post

class ChatGroq(BaseInference):
    def invoke(self, messages: list[BaseMessage],json:bool=False):
        self.headers.update({'Authorization': f'Bearer {self.api_key}'})
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "https://api.groq.com/openai/v1/chat/completions"
        payload={
            "model": self.model,
            "messages": [message.to_dict() for message in messages],
            "temperature": temperature,
            "stream":False,
        }
        if json:
            payload["response_format"]={
                "type": "json_object"
            }
        try:
            response=post(url=url,json=payload,headers=headers)
            json_object=response.json()
            # print(json_object)
            content=json_object['choices'][0]['message']['content']
            return AIMessage(content)
        except Exception as err:
            print(err)