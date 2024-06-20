from inference.base import BaseInference
from message.base import AIMessage
from requests import post

class Ollama(BaseInference):
    def invoke(self,messages: list[dict])->AIMessage:
        headers=self.headers
        temperature=self.temperature
        # stop=["Observation: "]
        url=self.base_url or "http://localhost:11434/api/chat"
        payload={
            "model": self.model,
            "messages": [message.to_dict() for message in messages],
            "options":{
                "temperature": temperature,
            },
            "format":"json",
            "stream":False
        }
        try:
            response=post(url=url,json=payload,headers=headers)
            response.raise_for_status()
            json_obj=response.json()
            return AIMessage(json_obj['message']['content'])
        except Exception as err:
            print(err)
    