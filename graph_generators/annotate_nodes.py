import os
from functools import reduce

from data_structures.graph import NodeType, ConnectionType, Graph, Node
import dotenv


def get_slash():
    return os.path.normpath("/")


class Annotator:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.in_progress: dict[str, bool] = dict()

    def get_function_annotation(self, node: Node) -> str:
        if node.node_type != NodeType.FUNCTION:
            return ""

        # check cache
        if node.description != "":
            return node.description

        # external libraries
        if node.path == "":
            node.description = "External node"
            return node.description

        # check for circular dependency
        if node.name in self.in_progress and self.in_progress[node.name]:
            file_content = ""
            with open(node.path, "r") as f:
                file_content = f.read()
            if file_content == "":
                print(f"ERROR: could not read file at {node.path}")
                return ""
            return file_content
        self.in_progress[node.name] = True

        # read file with the function
        file_content = ""
        with open(node.path, "r") as f:
            file_content = f.read()
        if file_content == "":
            print(f"ERROR: could not read file at {node.path}")
            return ""

        # get description of dependencies
        descriptions_of_functions_used = []
        for connection in node.connection:
            if connection.connection_type == ConnectionType.USES:
                other_node = connection.next_node
                descriptions_of_functions_used.append(
                    f"Description for {other_node.name}:\n{self.get_function_annotation(other_node)}"
                )

        # generate description with openai
        all_descriptions = reduce(lambda x, y: x + "\n\n" + y, descriptions_of_functions_used, "")
        response = annotate_file(file_content, all_descriptions)
        file_of_node = node.path.replace(self.graph.path_to_project + get_slash(), "").replace(get_slash(), ".").replace(".py", "")
        for function_description in response["function_descriptions"]:
            new_node_name = file_of_node + "." + function_description["name"]
            if new_node_name in self.graph.nodes:
                self.graph.nodes[new_node_name].description = function_description["description"]
            else:
                print(f"ERROR: Could not assign description to node {new_node_name}")

        for node_name, current_node in self.graph.nodes.items():
            if node_name.startswith(file_of_node) and current_node.description == "":
                if current_node.node_type == NodeType.FUNCTION:
                    current_node.description = "Function is defined in a parent class"

        if node.description == "":
            node.description = "Function is defined in a parent class"
        self.in_progress[node.name] = False
