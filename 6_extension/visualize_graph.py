from pyvis.network import Network
from graph import build_project_graph

def visualize_project(root_dir, output_html = 'project_graph.html'):
    G = build_project_graph(root_dir)
    net = Network(height= '750px', width = '100%', directed= True)
    colors = {'file': 'lightblue', 'class': 'lightgreen', 'function': 'lightcoral'}
    for node, attr in G.nodes(data=True):
        net.add_node(node, label = node, color = colors.get(attr.get('type')))
        
    for src, dst, attr in G.edges(data = True):
        net.add_edge(src, dst, title = attr.get('relation', ''), color = '#A0A0A0')

    net.write_html(output_html)
    print(f"Visualization saved to {output_html}")

if __name__ == "__main__":
    root_directory = '/Users/manvithgopu/Desktop/Ollama_Agents/6_extension'
    visualize_project(root_directory)