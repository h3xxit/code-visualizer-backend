from flask import Flask
from data_structures.graph import Graph
from graph_generators.file_graph_generator import create_complete_graph, create_packages_graph

app = Flask(__name__)
# path to Graph maps
complete_graphs: dict[str, Graph] = {}
packages_graphs: dict[str, Graph] = {}
files_classes_graphs: dict[str, dict[str,Graph]] = {}

@app.route("/graph/packages?project=<project>")
def get_packages_graph(project: str):
    if project in packages_graphs:
        return packages_graphs[project].model_dump_json()
    else:
        complete_graphs[project] = create_complete_graph(project)
        packages_graphs[project] = create_packages_graph(complete_graphs[project])
        files_classes_graphs[project] = create_files_classes_graphs(complete_graphs[project])
        return packages_graphs[project].model_dump_json()



@app.route("/graph/file-and-classes?project=<project>&package=<package>")
def get_files_and_classes_graph(project: str, package: str):
    return "<p>Hello, World!</p>"


@app.route("/graph/packages?project=<project>&file=<file>")
def get_function_graph(project: str, file: str):
    return "<p>Hello, World!</p>"

@app.route("/graph/packages?project=<project>&className=<className>")
def get_function_graph(project: str, className: str):
    return "<p>Hello, World!</p>"