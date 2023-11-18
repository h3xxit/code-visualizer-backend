from functools import reduce

from data_structures.graph import NodeType, ConnectionType, Graph, Node
from graph_generators.file_graph_generator import create_function_graph, get_slash
from graph_generators.openAiIntegration import annotate_file
import dotenv


class Annotator:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.in_progress: dict[str, bool] = dict()

    def get_function_annotation(self, node: Node) -> str:
        # check cache
        if node.description != "":
            return node.description

        # external libraries
        if node.path == "<external>":
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
                    "Description for " + other_node.name + ":\n" + self.get_function_annotation(other_node)
                )

        # generate description with openai
        all_descriptions = reduce(lambda x, y: x + "\n\n" + y, descriptions_of_functions_used, "")
        response = annotate_file(file_content, all_descriptions)
        for function_description in response["function_descriptions"]:
            new_node_name = node.path.replace(graph.path_to_project + get_slash(), "").replace(get_slash(), ".").replace(
                ".py", "") + "." + function_description["name"]
            if new_node_name in graph.nodes:
                graph.nodes[new_node_name].description = function_description["description"]
            else:
                print(f"ERROR: Could not assign description to node {new_node_name}")

        if node.description == "":
            node.description = "Function is defined in a parent class"
        self.in_progress[node.name] = False


if __name__ == "__main__":
    dotenv.load_dotenv()
    graph = create_function_graph("../test_project")
    annotator = Annotator(graph)

    annotator.get_function_annotation(graph.nodes["diagram.BaseNodes.StarterNode._getVariable"])
    with open("../graph.json", "w+") as f:
        f.write(graph.model_dump_json(indent=2))

