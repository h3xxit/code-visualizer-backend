from __future__ import annotations
from pydantic import BaseModel, field_serializer
from enum import Enum
import dotenv
import openai
from openai import chat
import json

dotenv.load_dotenv()
client = openai.OpenAI()
function_description_promt = "You will recieve a python file as input and a short description of each internal and external function which is called from the file. "+\
"Extract the defined functions and methods per class and summarize them in 2 short sentences."


class ConnectionType(Enum):
    DEFINES = 1
    CONTAINS = 2
    INHERITS_FROM = 3
    USES = 4

class NodeType(Enum):
    FILE = 1
    FUNCTION = 2
    CLASS = 3
    MODULE = 4


class Connection(BaseModel):
    next_node: Node
    connection_type: ConnectionType

    def __init__(self, next_node: Node, connection_type: str):
        super().__init__(next_node=next_node, connection_type=connection_type)

    @field_serializer("next_node")
    def serialize_next_node(self, next_node: Node):
        return next_node.name


class Node(BaseModel):
    name: str
    node_type: str
    description: str
    node_type : NodeType
    connection: list[Connection]
    path : str
    start_line = -1
    end_line = -1

    def __init__(self, name: str, node_type: NodeType, path: str):
        super().__init__(name=name, description="", node_type=node_type, connection=[], path=path)


class Graph(BaseModel):
    nodes: dict[str, Node]

    def __init__(self):
        super().__init__(nodes=dict())


    def annotate_functions(self):
        

        visited = set()

        for node_name, node in self.nodes.items():
            if node.node_type == NodeType.FILE:
                # open file
                with open(node.path, "r") as f:
                    file_content = f.read()
                    # attach called function descriptions to files
                    function_calls = ""

                    # search for function calls
                    conn_queue = node.connection.copy()
                    while len(conn_queue) > 0:
                        connection = conn_queue.pop(0)
                        if connection.connection_type == ConnectionType.DEFINES:
                            if connection.
                            for function in functions:
                                if function["name"] == connection.next_node.name:
                                    connection.next_node.description = function["description"]
                                    break


                   
                    conn_queue = node.connection.copy()
                    while len(conn_queue) > 0:
                        connection = conn_queue.pop(0)
                        if connection.connection_type == ConnectionType.DEFINES:
                            for function in functions:
                                if function["name"] == connection.next_node.name:
                                    connection.next_node.description = function["description"]
                                    break



def annotate_file(file_content: str, function_call_desc: str) -> list[dict[str, str]]:

    file_content = function_call_desc+file_content
    system_promt = [{"role": "system",
                        "content": function_description_promt,
                        "functions": [{"name": "create description",
                                        "description": "creates a descriptions functions and methods per class",
                                          "parameters":
                                            {"type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "name": {
                                                        "type": "string",
                                                        "minLength": 1
                                                    },
                                                    "description": {
                                                        "type": "string",
                                                        "minLength": 1
                                                    }
                                                },
                                                "required": ["name", "description"],}}}]}]

    response = client.chat.completions.create(
                        model="gpt-4-1106-preview",
                        messages=[system_promt, {"role": "user", "content": file_content}],
                        )  
                    
    json_response = response.choices[0].message.content["function_call"]["arguments"]
    functions: list[dict[str, str]] = json.loads(json_response)
    return functions