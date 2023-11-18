from functools import reduce

from data_structures.graph import NodeType, ConnectionType, Graph, Node
from graph_generators.file_graph_generator import create_function_graph
from graph_generators.openAiIntegration import annotate_file
import dotenv


class Annotator:
    def __init__(self, graph: Graph):
        self.graph = graph
        # self.completed: dict[str, bool] = dict()
        self.in_progress: dict[str, bool] = dict()

    def get_function_annotation(self, node: Node) -> str:
        # check cache
        if node.description == "":  # node.name in self.completed and self.completed[node.name]:
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
            described_node = function_description.name

        node.description = "Yes"
        # self.completed[node.name] = True


if __name__ == "__main__":
    dotenv.load_dotenv()
    graph = create_function_graph("../test_project")
    annotator = Annotator(graph)

    annotator.get_function_annotation(graph.nodes["diagram.BaseNodes.StarterNode._getVariable"])
