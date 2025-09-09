import ast
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from dotenv import load_dotenv
import os

load_dotenv()

nvidia_api_key = os.getenv("NVIDIA_API_KEY")
nvidia_model_name = os.getenv("NVIDIA_MODEL_NAME")

llm = ChatNVIDIA(
    model_name = nvidia_model_name,
    api_key = nvidia_api_key,
)

def extract_function_code(filepath, function_name):
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()               # Read the whole file
    tree = ast.parse(source, filename=filepath)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            # Pass the source string, not f.read()
            return ast.get_source_segment(source, node)
    return ""

def summarize_function(code):
    prompt = f"Explain what this python function does: \n {code}"
    response = llm.invoke(prompt)
    return response.content

if __name__ == "__main__":
    load_dotenv()
    file_path = '/Users/manvithgopu/Desktop/Ollama_Agents/6_extension/func_summarize.py'
    function_name = 'summarize_function'
    
    function_code = extract_function_code(file_path, function_name)
    if function_code:
        summary = summarize_function(function_code)
        print(f"Summary of function '{function_name}':\n{summary}")
    else:
        print(f"Function '{function_name}' not found in {file_path}.")