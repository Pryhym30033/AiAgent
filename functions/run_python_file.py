import os
import subprocess


def run_python_file(working_directory, file_path, args=None):
    fullPath = os.path.join(working_directory, file_path)

    if not os.path.abspath(fullPath).startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

    if not os.path.exists(os.path.abspath(fullPath)):
        return f'Error: File "{file_path}" not found.'

    if not file_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'
    

    
    try:
        arguments = ["python", os.path.abspath(fullPath)]

        if args:
            arguments.extend(args)

        results = subprocess.run(
            arguments,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.path.abspath(working_directory),
        )
        output =[]
        if results.stdout:
            output.append(f"STDOUT: \n{results.stdout}")

        if results.stderr:
            output.append(f"STDERR:\n{results.stderr}")

        if results.returncode != 0:
            output.append(f"Process exited with code {results.returncode}")
        
        return "\n".join(output) if output else "No output produced."

    except Exception as e:
        return f"Error: executing Python file: {e}"

