import os

def write_file(working_directory, file_path, content):
    fullPath = os.path.join(working_directory, file_path)

    if not os.path.abspath(fullPath).startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

    if not os.path.exists(fullPath):
        try:
            os.makedirs(os.path.dirname(fullPath), exist_ok=True)
        except Exception as e:
            print(f"Error: An unexpected error occurred: {e}")

    if os.path.exists(fullPath) and os.path.isdir(fullPath):
         return f'Error: "{file_path}" is a directory, not a file'    

    try:
        with open(fullPath, "w") as f:
            f.write(content)
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")

    return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'