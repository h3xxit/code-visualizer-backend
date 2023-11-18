import os

from data_structures.file_graph import FileGraph
from data_structures.project import Project, File, Module
from pycg.pycg import CallGraphGenerator
from pycg.utils.constants import CALL_GRAPH_OP
from pycg import formats
import json

def read_project_structure(absolute_path_to_project: str):
    project = Project()
    for (dirpath, dirnames, filenames) in os.walk(absolute_path_to_project):
        for filename in filenames:
            if filename.endswith(".py"):
                relative_dirpath = dirpath#dirpath.replace(absolute_path_to_project, ".")
                if filename != "__init__.py":

                    #project.files[relative_dirpath] = Module(os.path.basename(relative_dirpath), os.path.dirname(relative_dirpath))
                #else:
                    project.files[os.path.join(relative_dirpath, filename)] = File(filename, os.path.join(relative_dirpath, filename))
    return project


def parseFileImports(file: File, project: Project):
    pass


def create_file_graph(absolute_path_to_project: str, fastenFormat: bool):
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
        f.write(json.dumps(output))



create_file_graph("../test_project", True)