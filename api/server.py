from flask import Flask
from flask_cors import CORS
from data_structures.graph import Graph
from graph_generators.file_graph_generator import create_complete_graph, create_packages_graph, create_files_classes_graphs, create_function_graph

app = Flask(__name__)
CORS(app, origins="*")
# path to Graph maps
complete_graphs: dict[str, Graph] = {}
packages_graphs: dict[str, Graph] = {}
files_classes_graphs: dict[str, dict[str,Graph]] = {}

@app.route("/graph/packages?project=<project>")
def get_packages_graph(project: str):
    if project not in packages_graphs:
        complete_graphs[project] = create_complete_graph(project)
        packages_graphs[project] = create_packages_graph(complete_graphs[project])
    return packages_graphs[project].model_dump_json()

@app.route("/graph/complete?project=<project>")
def get_complete_graph(project: str):
    if project not in complete_graphs:
        complete_graphs[project] = create_complete_graph(project)
        packages_graphs[project] = create_packages_graph(complete_graphs[project])
    return complete_graphs[project].model_dump_json()


@app.route("/graph/file-and-classes?project=<project>&package=<package>")
def get_files_and_classes_graph(project: str, package: str):
    if project not in complete_graphs: 
        complete_graphs[project] = create_complete_graph(project)
        packages_graphs[project] = create_packages_graph(complete_graphs[project])
    return create_files_classes_graphs(complete_graphs[project], package).model_dump_json()
    

@app.route("/graph/packages?project=<project>&className=<className>")
def get_function_graph(project: str, className: str):
    if project not in complete_graphs: 
        complete_graphs[project] = create_complete_graph(project)
        packages_graphs[project] = create_packages_graph(complete_graphs[project])
    return create_function_graph(complete_graphs[project], className).model_dump_json() 

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000)