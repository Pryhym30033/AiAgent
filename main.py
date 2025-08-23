import os
import sys
from functions.get_file_content import *
from functions.get_files_info import *
from functions.run_python_file import *
from functions.write_file import *
from dotenv import load_dotenv
from google import genai
from google.genai import types


system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory, lists files in the working directory itself.",     
            ),
        },
    ),
)


schema_get_files_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Receives the contents from a file as a string and inputs it into the LLM, constrained to the working directory.", 
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="path to the file with the content to be read, the file will be in the working directory.",
            ),
        },
    ),
)


schema_run_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs file within the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="path to the file with the content to be read, the file will be in the working directory.",
            ),
            "args": types.Schema(
                type=types.Type.STRING,
                description="lists the file type if given.",
            ),
        },
    ),
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="writes or over writes and lists the contents and files written by the function, the file will exist with in the working directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="path to the file to be written or over written, the file will be in the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="lists the contents of the file to be written or over written."
            ),
        },
    ),
)


available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_files_content,
        schema_run_file,
        schema_write_file,
    ]
)

def  call_function(function_call_part, verbose=False):
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")

    functionMap = {}
    functionMap["get_file_content"] = get_file_content
    functionMap["get_files_info"] = get_files_info
    functionMap["run_python_file"] = run_python_file
    functionMap["write_file"] = write_file

    function_call_part.args["working_directory"] = "./calculator"

    if function_call_part.name not in functionMap:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"error": f"Unknown function: {function_call_part.name}"},
                )
            ],
        )
    
    function = functionMap[function_call_part.name]
    result = function(** function_call_part.args)

    return types.Content(
    role="tool",
    parts=[
        types.Part.from_function_response(
            name=function_call_part.name,
            response={"result": result},
        )
    ],
)
     
def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    input = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
    verbose = "--verbose" in sys.argv

    if not input:
        print("AI Code Assistant")
        print('\nUsage: python main.py "your prompt here" [--verbose]')
        print('Example: python main.py "How do I build a calculator app?"')
        sys.exit(1)

    userPrompt = " ".join(input)

    if verbose:
        print(f"User prompt: {userPrompt}\n")

    messages = [
        types.Content(role="user", parts=[types.Part(text=userPrompt)]),
    ]

    generateContent(client, messages, verbose)

def generateContent(client, messages, verbose):
    response = client.models.generate_content(
        model="gemini-2.0-flash-001", 
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
            ),
    )
    if verbose:
        print("Prompt tokens:", response.usage_metadata.prompt_token_count)
        print("Response tokens:", response.usage_metadata.candidates_token_count)


    if response.function_calls:
        for function in response.function_calls:
            result = call_function(function, verbose=verbose)
            if (result.parts and
                hasattr(result.parts[0], "function_response") and
                hasattr(result.parts[0].function_response, "response")):
                if verbose:
                    print(f"-> {result.parts[0].function_response.response}")
            else:
                raise Exception("Fatal error: function response missing!")



if __name__ == "__main__":
    main()