import ast
from collections import defaultdict

class FileAnalysis:
    def __init__(self, file_path):
        self.file_path = file_path
        self.imports = []
        self.import_from = {}
        self.functions =[]
        self.classes = []


def analyze_file(filepath):
    with open(filepath, 'r', encoding = 'utf-8') as f:
        tree = ast.parse(f.read(), filename=filepath)

    import_from_dict = defaultdict(list)
    analysis = FileAnalysis(file_path=filepath)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                analysis.imports.append(n.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module
            for n in node.names:
                import_from_dict[mod].append(n.name)
            # analysis.imports.append(node.module)
        elif isinstance(node, ast.FunctionDef):
            analysis.functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            analysis.classes.append(node.name)

    analysis.import_from = dict(import_from_dict)

    return analysis


if __name__ == "__main__":
    result = analyze_file('/Users/manvithgopu/Desktop/Ollama_Agents/3_voice_try_2/chatbot.py')
    print("Imports: ", result.imports)
    print("Import From: ", result.import_from)
    print("Functions: ",result.functions)
    print("Classes: ",result.classes)