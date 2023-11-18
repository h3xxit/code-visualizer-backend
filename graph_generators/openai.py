import dotenv
import openai
import json

from data_structures.graph import NodeType, ConnectionType, Graph

dotenv.load_dotenv()
client = openai.OpenAI()
function_description_promt = "You will recieve a python file as input and a short description of each internal and external function which is called from the file. " + \
                             "Extract the defined functions and methods per class and summarize them in 2 short sentences."

def annotate_functions(graph: Graph):
    visited = set()

    for node_name, node in graph.nodes.items():
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
                        # if connection.
                        # for function in functions:
                        #    if function["name"] == connection.next_node.name:
                        #        connection.next_node.description = function["description"]
                        break

                conn_queue = node.connection.copy()
                while len(conn_queue) > 0:
                    connection = conn_queue.pop(0)
                    if connection.connection_type == ConnectionType.DEFINES:
                        # for function in functions:
                        #    if function["name"] == connection.next_node.name:
                        #        connection.next_node.description = function["description"]
                        break


def annotate_file(file_content: str, function_call_desc: str) -> list[dict[str, str]]:
    file_content = function_call_desc + file_content
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
                                             "required": ["name", "description"], }}}]}]

    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[system_promt, {"role": "user", "content": file_content}],
    )

    json_response = response.choices[0].message.content["function_call"]["arguments"]
    functions: list[dict[str, str]] = json.loads(json_response)
    return functions
