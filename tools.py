from tool.base import tool
from pydantic import BaseModel,Field
from random import randint
from os.path import join
from subprocess import run

class Terminal(BaseModel):
    cmd:str=Field(...,description="The command to be executed.")

@tool('Terminal Tool',Terminal)
def terminal_tool(cmd):
    '''This Tool is used to execute terminal commands.'''
    process=run(cmd,text=True,shell=True,capture_output=True)
    if process.returncode!=0:
        return process.stderr.strip()
    else:
        return process.stdout.strip()

class Weather(BaseModel):
    location:str=Field(...,description="The location for the weather.")

@tool('Weather Tool',Weather)
def weather_tool(location):
    '''This Tool is used to give weather for a location.'''
    return f"{location} is at {randint(20,40)} deg celsius"

class Random(BaseModel):
    pass

@tool('Random Number Tool',Random)
def random_gen_tool():
    '''This Tool is used to generate random numbers only.'''
    return f"Random Number: {randint(0,100)}"

class Save(BaseModel):
    file_path:str=Field(...,description='file path of the file.')
    filename:str=Field(...,description='filename of the file.')
    content:str=Field(...,description='the content that wanted to be saved.')

@tool("Save Tool",args_schema=Save)
def save_tool(file_path,filename,content)->str:
    '''This tool is used to save the contents to a file.
    example: save_tool('./foo/bar/','abc.py','Hello World')
    '''
    with open(join(file_path,filename),'w') as f:
        f.write(content)
    return f"Saved {filename} in {file_path} successfully."