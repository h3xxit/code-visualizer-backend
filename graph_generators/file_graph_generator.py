import os

from data_structures.file_graph import FileGraph
from data_structures.project import Project, File, Module


def read_project_structure(absolute_path_to_project: str):
    project = Project()
    for (dirpath, dirnames, filenames) in os.walk(absolute_path_to_project):
        for filename in filenames:
            if filename.endswith(".py"):
                relative_dirpath = dirpath.replace(absolute_path_to_project, ".")
                if filename == "__init__.py":
                    project.files[relative_dirpath] = Module(os.path.basename(relative_dirpath), os.path.dirname(relative_dirpath))
                else:
                    project.files[os.path.join(relative_dirpath, filename)] = File(filename, os.path.join(relative_dirpath, filename))
    return project


def parseFileImports(file: File, project: Project):
    pass


def create_file_graph(absolute_path_to_project: str):
    fileGraph = FileGraph()
    project: Project = read_project_structure(absolute_path_to_project)
    for file in project.files.values():
        if isinstance(file, File):
            parseFileImports(file, project)
        elif isinstance(file, Module):
            pass
    pass


create_file_graph("../test_project")