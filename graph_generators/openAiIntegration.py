import openai
import json

function_description_promt = "You will recieve the code of a python file as input and a short description of each internal and external function which is called from the code. " + \
                             "Extract the functions and methods defined in the code and summarize each of them in 2 short sentences."

ask_graph_prompt = "You are a chatbot that a user can interact with and code architecture expert. The chat is part of an application that gives a graphical overview of a python code repository at different granularities. " + \
    "The repository is presented as a graph of nodes where a node can either be a module, a file, a class or a function. You will recieve the message of the user and the currently displayed graph as json input. " + \
    "Answer the message of theuser according to currently displayed graph while taking previously asked questions and graphs into account. If you refer to a node in your answer, use the name of the node and wrap it " + \
    "in double curly brackets, e.g. {{node_name}}." 
    
def annotate_file(file_content: str, function_call_desc: str) -> dict[str, list]:
    file_content = f"Code: \n{file_content}\nRelated functions:\n{function_call_desc}"
    system_prompt = {
        "role": "system",
        "content": function_description_promt,
    }
    tools = [
        {
            "type": "function",
            "function": {
                "name": "function_description_reader",
                "description": "Describes each function and method in the provided code in 2 short sentences. The name should be prefixed by the class name, in the format 'class.function_name'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "function_descriptions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "type": "string",
                                        "minLength": 1
                                    },
                                    "description": {
                                        "type": "string",
                                        "minLength": 1
                                    }
                                },
                                "required": ["name", "description"],
                            }
                        }
                    }
                }
            }
        }
    ]

    print("Made a request to openAI")
    response = openai.OpenAI().chat.completions.create(
        model="gpt-3.5-turbo",#"gpt-4-1106-preview",
        messages=[system_prompt, {"role": "user", "content": file_content}],
        tools=tools, temperature=0.,
    )
    print("Finished openAI request")

    json_response = response.choices[0].message.tool_calls[0].function.arguments
    functions: dict[str, list] = json.loads(json_response)
    return functions


def ai_query_with_graph(graph_str: str, messages: list[any], current_level: str):
    system_prompt = {
        "role": "system",
        "content": ask_graph_prompt,
    }
    
    
    messages = [system_prompt]+(messages[:-1])+([{"role": "user", "content": graph_str}])+ [{"role": "system", "content": f"the user is currently displayed the {current_level}"}]+([messages[-1]])

    response = openai.OpenAI().chat.completions.create(
        model="gpt-3.5-turbo",#"gpt-4-1106-preview",
        messages=messages,
        temperature=0.,
    )

    ai_response = response.choices[0].message.content
    return ai_response
