import openai
import json

function_description_promt = "You will recieve the code of a python file as input and a short description of each internal and external function which is called from the code. " + \
                             "Extract the functions and methods defined in the code and summarize each of them in 2 short sentences."

ask_graph_prompt = "You are a chatbot that a user can interact with. the chat is part of an application that gives a graphical overview of a python code repository at different granularities. " + \
    "The repository is presented as a graph of nodes where a node can either be a module, a file, a class or a function. You will recieve the message of the user and the currently displayed graph as json input. " + \
    "Answer the message of theuser according to currently displayed graph while taking previously asked questions and graphs into account. If you refer to a node in your answer, use the name of the node and wrap it " + \
    "in double curly brackets, e.g. {{node_name}}." 


def annotate_file(file_content: str) -> str:
    file_content = f"Code: \n{file_content}\n"
    system_prompt = {
        "role": "system",
        "content": "You will recieve the code of a python file as input. Reply in 2 short sentences with a description of everything the file does. Your reply MUST NOT have more than 300 characters. " +
                   "This is an example of a class description: 'The file defines classes for creating conversational agents and managing their interactions. The `AutoGenAgentNode` class is an abstract base class for creating agents with specific configurations. The `AutoGenAssistantAgentNode` and `AutoGenUserProxyNode` classes inherit from `AutoGenAgentNode` and implement the `createAgent` method to create specific types of agents. The `AutoGenTwoAgentConversation` and `AutoGenGroupChat` classes manage conversations between two agents and a group of agents respectively.'",
    }
    print("Made a request to openAI")
    response = openai.OpenAI().chat.completions.create(
        model="gpt-3.5-turbo",#"gpt-4-1106-preview",
        messages=[system_prompt, {"role": "user", "content": file_content}],
        temperature=0.,
    )
    print("Finished openAI request")

    return response.choices[0].message.content


def annotate_class(file_content: str, class_name: str) -> str:
    file_content = f"Code: \n{file_content}\nClass:\n{class_name}"
    system_prompt = {
        "role": "system",
        "content": "You will recieve the code of a python file as input, and a class name. Reply in 2 short sentences with a description of what the class does. Your reply MUST NOT have more than 300 characters." +
                   "This is an example of a class description: 'The OpenAiChatHistoryNode class in Python is a type of StarterNode that manages the history of a chat conversation. It has a run method that returns a dictionary containing the chat history. The class is used to append new chat items to the existing history and return the updated history.'",
    }
    print("Made a request to openAI")
    response = openai.OpenAI().chat.completions.create(
        model="gpt-3.5-turbo",#"gpt-4-1106-preview",
        messages=[system_prompt, {"role": "user", "content": file_content}],
        temperature=0.,
    )
    print("Finished openAI request")

    return response.choices[0].message.content


def annotate_functions_in_file(file_content: str, function_call_desc: str) -> dict[str, list]:
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
        model="gpt-4-1106-preview",
        messages=[system_prompt, {"role": "user", "content": file_content}],
        tools=tools, temperature=0.,
    )
    print("Finished openAI request")

    json_response = response.choices[0].message.tool_calls[0].function.arguments
    functions: dict[str, list] = json.loads(json_response)
    return functions


def ai_quiry_with_graph(graph_str: str, messages : list[str]):
    system_prompt = {
        "role": "system",
        "content": ask_graph_prompt,
    }

    print("Made a request to openAI")
    response = openai.OpenAI().chat.completions.create(
        model="gpt-3.5-turbo",#"gpt-4-1106-previewprint",
        messages=[system_prompt, {"role": "user", "content": graph_str}, {"role": "user", "content": messages}],
        temperature=0.,
    )
    print("Finished openAI request")

    ai_response = response.choices[0].message.content
    return json_response