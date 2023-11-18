import openai
import json

from openai.types.chat import ChatCompletionFunctionMessageParam

function_description_promt = "You will recieve the code of a python file as input and a short description of each internal and external function which is called from the code. " + \
                             "Extract the functions and methods defined in the code and summarize each of them in 2 short sentences."


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
                "description": "Describes each function and method in the provided code in 2 short sentences. The name should be prefixed by the class name, if the method is in a class.",
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
        tools=tools
    )
    print("Finished openAI request")

    json_response = response.choices[0].message["tool_calls"][0]["function"]["arguments"]
    functions: dict[str, list] = json.loads(json_response)
    return functions
