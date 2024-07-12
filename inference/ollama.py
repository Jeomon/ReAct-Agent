from inference.base import BaseInference
from message.base import AIMessage
from requests import post
from json import loads
from typing import Literal

class ChatOllama(BaseInference):
    def invoke(self,messages: list[dict],stream=False,format:Literal['','json']='')->AIMessage:
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "http://localhost:11434/api/chat"
        payload={
            "model": self.model,
            "messages": [message.to_dict() for message in messages],
            "options":{
                "temperature": temperature,
            },
            "format":format,
            "stream":stream
        }
        try:
            response=post(url=url,json=payload,headers=headers)
            response.raise_for_status()
            json_obj=response.json()
            return AIMessage(json_obj['message']['content'])
        except Exception as err:
            print(err)
    
    def stream(self,messages: list[dict],format:Literal['','json']=''):
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "http://localhost:11434/api/chat"
        payload={
            "model": self.model,
            "messages": [message.to_dict() for message in messages],
            "options":{
                "temperature": temperature,
            },
            "format":format,
            "stream":True
        }
        try:
            response=post(url=url,json=payload,headers=headers,stream=True)
            response.raise_for_status()
            chunks=response.iter_lines(decode_unicode=True)
            for chunk in chunks:
                yield loads(chunk)
        except Exception as err:
            print(err)

class Ollama(BaseInference):
    def invoke(self, query:str,format:Literal['','json']='')->AIMessage:
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "http://localhost:11434/api/generate"
        payload={
            "model": self.model,
            "prompt": query,
            "options":{
                "temperature": temperature,
            },
            "format":format,
            "stream":False
        }
        try:
            response=post(url=url,json=payload,headers=headers)
            response.raise_for_status()
            json_obj=response.json()
            return AIMessage(json_obj['response'])
        except Exception as err:
            print(err)

    def stream(self,query:str,format:Literal['','json']=''):
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "http://localhost:11434/api/generate"
        payload={
            "model": self.model,
            "prompt": query,
            "options":{
                "temperature": temperature,
            },
            "format":format,
            "stream":True
        }
        try:
            response=post(url=url,json=payload,headers=headers,stream=True)
            response.raise_for_status()
            chunks=response.iter_lines(decode_unicode=True)
            for chunk in chunks:
                yield loads(chunk)
        except Exception as err:
            print(err)
