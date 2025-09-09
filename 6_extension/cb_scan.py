import os

def find_python_files(root_dir):
    """ Finds all the python files in the root directory """
    py_files = []
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(subdir, file))

    return py_files

if __name__ == "__main__":
    root_directory = "/Users/manvithgopu/Desktop/Ollama_Agents/5_MCP"
    python_files = find_python_files(root_directory)
    
    if python_files:
        print("Python files found:")
        for file in python_files:
            print(file)
    else:
        print("No Python files found.")
