import networkx as nx
from cb_scan import find_python_files
from code_analyzer import analyze_file

import os
print("Current working directory:", os.getcwd())

def build_project_graph(root_dir):
    G = nx.DiGraph()
    files = find_python_files(root_dir)

    for file in files:
        # abs_path = os.path.join(root_dir, file)
        # if not os.path.isabs(file):
        #     abs_path = os.path.join(root_dir, file)
        # else:
        #     abs_path = file
        fa = analyze_file(file)
        G.add_node(file, type = 'file')
        for imp in fa.imports:
            G.add_edge(file, imp, relation= 'import')
        for mod, names in fa.import_from.items():
            G.add_edge(file, mod, relation = 'import_from')
            for name in names:
                G.add_edge(file, f"{mod}.{name}", relation = 'import_from_item')
        for cls in fa.classes:
            G.add_node(cls, type = 'class', file = file)
            G.add_edge(file, cls, relation= 'defines')
        for func in fa.functions:
            G.add_node(func, type = 'function', file = file)
            G.add_edge(file, func, relation = 'defines')
    
    return G


if __name__ == "__main__":
    root_directory = '/Users/manvithgopu/Desktop/Ollama_Agents/6_extension'
    project_graph = build_project_graph(root_directory)
    
    # Example of printing the graph
    print("Nodes in the graph:")
    for node in project_graph.nodes(data=True):
        print("Nodes of the graph are: ")
        print(node)
    
    print("\nEdges in the graph:")
    for edge in project_graph.edges(data=True):
        print(edge)

