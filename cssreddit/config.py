import json


class Config:
    def __init__(self, path: str):
        with open(path, newline='\n') as f:
            data = json.load(f)
            self.input = data['input']
            self.output = data['output']
            self.filter = data['filter']
            self.sub_groups = data['sub_groups']
