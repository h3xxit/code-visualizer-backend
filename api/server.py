from flask import Flask

app = Flask(__name__)

@app.route("/graph/packages?project=<project>")
def get_packages_graph(project: str):
    return "<p>Hello, World!</p>"


@app.route("/graph/file-and-classes?project=<project>&package=<package>")
def get_files_and_classes_graph(project: str, package: str):
    return "<p>Hello, World!</p>"


@app.route("/graph/packages?project=<project>&package=<package>")
def get_function_graph(project: str, package: str):
    return "<p>Hello, World!</p>"