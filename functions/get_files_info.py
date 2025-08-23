import os

def get_files_info(working_directory, directory="."):
    fullPath = os.path.join(working_directory, directory)   
    
    if os.path.abspath(working_directory) not in os.path.abspath(fullPath):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

    if not os.path.isdir(fullPath):
        return f'Error: "{directory}" is not a directory'
    
    files = os.listdir(fullPath)
    output = f"Results for  '{directory}' directory:\n"
    for file in files:
        output += f" - {file}: file_size={os.path.getsize(os.path.join(fullPath, file))} bytes, is_dir={os.path.isdir(os.path.join(fullPath, file))}\n"
       
    return output
