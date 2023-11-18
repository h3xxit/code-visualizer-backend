import os
from typing import Optional

from data_structures.graph import Graph, Node, Connection, NodeType, ConnectionType
from data_structures.project import Project, File, Module
from pycg.pycg import CallGraphGenerator
from pycg.utils.constants import CALL_GRAPH_OP
from pycg import formats
import json


def read_project_structure(absolute_path_to_project: str) -> Project:
    project = Project()
    for (dirpath, dirnames, filenames) in os.walk(absolute_path_to_project):
        for filename in filenames:
            if filename.endswith(".py"):
                relative_dirpath = dirpath
                project.files[os.path.join(relative_dirpath, filename)] = File(filename,
                                                                               os.path.join(relative_dirpath, filename))
    return project


def parseFileImports(file: File, project: Project):
    pass


def dump_call_function_json(absolute_path_to_project: str, fastenFormat: bool):
    entry_points = read_project_structure(absolute_path_to_project).files.keys()
    callGraph = CallGraphGenerator(
        entry_points, absolute_path_to_project, -1, CALL_GRAPH_OP
    )
    callGraph.analyze()
    if fastenFormat:
        formatter = formats.Fasten(
            callGraph, None, "", "", "", ""
        )
    else:
        formatter = formats.Simple(callGraph)
    output = formatter.generate()
    with open("../graph.json", "w+") as f:
        f.write(json.dumps(output, indent=2))


def fix_slash_naming(inconsistent_name: str) -> str:
    return inconsistent_name.replace("\\", ".").replace("/", ".")


def filter_functions(function_graph: Graph, prefix: str) -> Graph:
    filtered_function_graph = Graph()
    for node_name, node in function_graph.nodes.items():
        if node_name.startswith(prefix):
            filtered_function_graph.nodes[node_name] = node
    return filtered_function_graph


def fix_naming_inconsistencies(output: dict[str, list[str]]) -> dict[str, list[str]]:
    consistent_output: dict[str, list[str]] = dict()
    for key, value in output.items():
        new_key = fix_slash_naming(key)
        if new_key in consistent_output:
            consistent_output[new_key] += list(fix_slash_naming(out) for out in output[key])
        else:
            consistent_output[new_key] = list(fix_slash_naming(out) for out in output[key])
    return consistent_output


def add_parent_nodes(absolute_path_to_project: str, node_name: str, project: Project, function_graph: Graph,
                     path_of_file_containing_node: str):
    path = absolute_path_to_project + "\\" + node_name.replace(".", "\\") + ".py"
    current_node = node_name
    while path not in project.files and path != ".py":
        new_path = os.path.dirname(path) + ".py"
        new_node = new_path.replace(absolute_path_to_project + "\\", "").replace("\\", ".").replace(".py", "")
        if new_path not in project.files:
            function_graph.nodes[new_node] = Node(new_node, NodeType.CLASS, path_of_file_containing_node)
        else:
            function_graph.nodes[new_node] = Node(new_node, NodeType.FILE, path_of_file_containing_node)
        function_graph.nodes[new_node].connection.append(
            Connection(function_graph.nodes[current_node], ConnectionType.DEFINES))
        path = new_path
        current_node = new_node


def add_file_class_and_functions(function_graph: Graph, consistent_output: dict[str, list[str]],
                                 absolute_path_to_project: str, project: Project):
    for node_name in consistent_output.keys():
        file_path = absolute_path_to_project + "\\" + node_name.replace(".", "\\") + ".py"
        while file_path not in project.files and file_path != ".py":
            file_path = os.path.dirname(file_path) + ".py"
        if file_path == ".py":
            file_path = ""
        if node_name not in function_graph.nodes:
            function_graph.nodes[node_name] = Node(node_name, NodeType.FUNCTION, file_path)

        if len(function_graph.nodes[node_name].connection) == 0:
            add_parent_nodes(absolute_path_to_project, node_name, project, function_graph, file_path)


def get_parent_package(absolute_path_to_project: str, path: str, project: Project, function_graph: Graph) -> Optional[
    Node]:
    new_path = os.path.dirname(path)
    new_node = new_path.replace(absolute_path_to_project + "\\", "").replace("\\", ".")
    if new_path == "":
        return None
    if new_path + "\\__init__.py" in project.files:
        if new_node not in function_graph.nodes:
            function_graph.nodes[new_node] = Node(new_node, NodeType.MODULE, new_path + "\\__init__.py")
        if len(function_graph.nodes[new_node].connection) == 0:
            parent_package = get_parent_package(absolute_path_to_project, new_path, project, function_graph)
            if parent_package is not None:
                parent_package.connection.append(Connection(function_graph.nodes[new_node], ConnectionType.CONTAINS))
                function_graph.nodes[new_node].parent_module = parent_package
        return function_graph.nodes[new_node]
    return get_parent_package(absolute_path_to_project, new_path, project, function_graph)


def create_function_graph(absolute_path_to_project: str):
    absolute_path_to_project = os.path.normpath(absolute_path_to_project)
    project: Project = read_project_structure(absolute_path_to_project)
    entry_points = project.files.keys()
    call_graph = CallGraphGenerator(
        entry_points, absolute_path_to_project, -1, CALL_GRAPH_OP
    )
    call_graph.analyze()
    formatter = formats.Simple(call_graph)
    output: dict[str, list[str]] = formatter.generate()
    consistent_output: dict[str, list[str]] = fix_naming_inconsistencies(output)

    function_graph = Graph()
    add_file_class_and_functions(function_graph, consistent_output, absolute_path_to_project, project)

    file_nodes = list(node for node in function_graph.nodes.values() if node.node_type == NodeType.FILE)
    for node in file_nodes:
        parent_package = get_parent_package(absolute_path_to_project, node.path, project, function_graph)
        if parent_package is not None:
            parent_package.connection.append(Connection(node, ConnectionType.CONTAINS))
            node.parent_module = parent_package

    for node_name, dependencies in consistent_output.items():
        for dependency in dependencies:
            function_graph.nodes[node_name].connection.append(
                Connection(function_graph.nodes[dependency], ConnectionType.USES))

    with open("../graph.json", "w+") as f:
        f.write(filter_functions(function_graph, "diagram").model_dump_json(indent=2))
        # f.write(function_graph.model_dump_json(indent=2))


# dump_call_function_json("../test_project", False)
create_function_graph("../test_project")
