from flask import Flask, jsonify, request
from flask import logging
from flask_cors import CORS
from data_structures.graph import Graph
from graph_generators.file_graph_generator import create_complete_graph, create_packages_graph, create_files_classes_graphs, create_function_graph
from graph_generators.openAiIntegration import ai_query_with_graph

app = Flask(__name__)
logger = logging.create_logger(app)
CORS(app, origins="*")
# path to Graph maps
complete_graphs: dict[str, Graph] = {}
packages_graphs: dict[str, Graph] = {}

def create_graph_if_empty(project: str):
    if project not in complete_graphs:
        complete_graphs[project] = create_complete_graph(project)
        packages_graphs[project] = create_packages_graph(complete_graphs[project])

@app.route("/graph/packages/<project>")
def get_packages_graph(project: str):
    create_graph_if_empty(project)
    return packages_graphs[project].model_dump_json()

@app.route("/graph/complete/<project>")
def get_complete_graph(project: str):
    create_graph_if_empty(project)
    return complete_graphs[project].model_dump_json()


@app.route("/graph/file-and-classes/<project>/<package>")
def get_files_and_classes_graph(project: str, package: str):
    create_graph_if_empty(project)
    return create_files_classes_graphs(complete_graphs[project], package).model_dump_json()
    

@app.route("/graph/function/<project>/<className>")
def get_function_graph(project: str, className: str):
    create_graph_if_empty(project)
    return create_function_graph(complete_graphs[project], className).model_dump_json() 

@app.route("/ask/<project>/<package>", methods=["POST"])
def ask_package(project: str, package: str):
    create_graph_if_empty(project)
    try:
        # Get the JSON data from the request body
       
        data = request.get_json()
        # Ensure that the 'data' key is present and contains a list
        if 'data' in data:
            messages = []
            current_level = data["data"]["current_level"]
            # Iterate through the list of objects
            for obj in data['data']["messages"]:
                # Ensure that each object has 'role' and 'message' fields
                if 'role' in obj and 'content' in obj:
                    role = obj['role']
                    message = obj['content']
                    
                    # Process the role and message as needed (you can customize this part)
                    
                    # Store the role and message in a list
                    messages.append({'role': role, 'content': message})
                else:
                    # If an object is missing 'role' or 'message', return an error response
                    return jsonify({'error': 'Each object must have "role" and "content" fields'}), 400

            # Process the list of messages as needed (you can customize this part)

            # Return a success response
            return ai_query_with_graph(packages_graphs[project].model_dump_json(), messages, current_level)
        else:
            # If 'data' key is missing or doesn't contain a list, return an error response
            return jsonify({'error': 'Invalid data format'}), 400

    except Exception as e:
        # Handle any exceptions that might occur during processing
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000, debug=True)