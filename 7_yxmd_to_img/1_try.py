import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import networkx as nx

def visualize_yxmd(file_path):
    # Parse the XML from the .yxmd file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Extract tool positions
    positions = {}
    for node in root.find('Nodes'):
        tool_id = node.attrib['ToolID']
        position = node.find('GuiSettings').find('Position')
        x = int(position.attrib['x'])
        y = int(position.attrib['y'])
        positions[tool_id] = (x, -y)  # Flip y for better visual orientation
    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes with positions
    for tool_id, pos in positions.items():
        G.add_node(tool_id, pos=pos)

    # Add edges based on connections
    for conn in root.find('Connections'):
        origin = conn.find('Origin').attrib['ToolID']
        destination = conn.find('Destination').attrib['ToolID']
        G.add_edge(origin, destination)

    # Draw the graph
    pos = nx.get_node_attributes(G, 'pos')
    nx.draw(G, pos, with_labels=True, node_size=2000, node_color='skyblue',
            font_size=10, font_weight='bold', arrows=True)
    plt.title("Alteryx Workflow Visualization")
    plt.show()

# Example usage:
# visualize_yxmd("path_to_your_file.yxmd")

if __name__ == "__main__":
    visualize_yxmd("C:\\Users\\10839330\\OneDrive - LTIMindtree\\Desktop\\Ollama_Agents\\7_yxmd_to_img\\sorting_snowflake_data.yxmd")
