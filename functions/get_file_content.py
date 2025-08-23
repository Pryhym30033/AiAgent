import os

def get_file_content(working_directory, file_path):
    fullPath = os.path.join(working_directory, file_path)

    if not os.path.abspath(fullPath).startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    
    if not os.path.isfile(fullPath):
        return f'Error: File not found or is not a regular file: "{file_path}"'
    
    try:
        with open(fullPath, "r") as f:
            contents = f.read()
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")
        
    if len(contents) > 1000:
        contents = contents[:10000]+f" [...File '{file_path}' truncated at 1000 characters]"
    
    return contents