import os
import json
import xml.etree.ElementTree as ET
import csv


def folders_list_assess(folder_path):
    subfolders=[]
    for item in os.listdir(folder_path):
        item_path=os.path.join(folder_path,item)
        if os.path.isdir(item_path):
            subfolders.append(item)
    return subfolders

def files_list_assess(folder_path):
    assess_files=[]
    for root,dirs,files in os.walk(folder_path):
        for file in files:
            if file.endswith(".yxmd"):
                assess_files.append(file)
    return assess_files

def load_json_file(json_file):
   with open(json_file, 'r') as file:
       return json.load(file)

# Function to calculate the complexity score of a workflow
def calculate_complexity_score(transformation_counts, join_info, lines_of_code, complexity_weights):
   total_score = 0
   # Calculate score based on transformations
   for transformation, count in transformation_counts.items():
       if transformation in complexity_weights['transformations']:
           total_score += count * complexity_weights['transformations'][transformation]
   # Calculate score based on number of joins
   total_score += len(join_info) * complexity_weights['joins']
   # Calculate score based on lines of code
   total_score += lines_of_code * complexity_weights['lines_of_code']
   return total_score

def count_total_nodes(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        node_count = len(root.findall('.//Node'))
        return node_count
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return 0
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0

# Extract transformation information from XML
def extract_transformations_from_xml(xml_file):
    possible_transformations_file=os.path.join(os.getcwd(),'static','assets','analyzer','plugin_to_transformation.json')
    not_possible_transformations_file=os.path.join(os.getcwd(),'static','assets','analyzer','not_possible_transformation.json')
    possible_transformations = load_json_file(possible_transformations_file)
    not_possible_transformations = load_json_file(not_possible_transformations_file)
    # possible_transformations = load_json_file('./plugin_to_transformation.json')
    # not_possible_transformations = load_json_file('./not_possible_transformation.json')
    
    transformation_counts = {}
    not_possible_transformations_counts = {}
    a=0
    b=0
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    for node in root.findall(".//Node"):
        gui_settings = node.find(".//GuiSettings")
        if gui_settings is not None:
            plugin = gui_settings.get("Plugin")
            if plugin in possible_transformations:
                a = a+1
                transformation = possible_transformations[plugin]
                if transformation in transformation_counts:
                    transformation_counts[transformation] += 1
                else:
                    transformation_counts[transformation] = 1
            else:
                if plugin in not_possible_transformations:
                    b = b+1
                    transformation = not_possible_transformations[plugin]
                    if transformation in not_possible_transformations_counts:
                        not_possible_transformations_counts[transformation] += 1
                    else:
                        not_possible_transformations_counts[transformation] = 1
    
    return transformation_counts, not_possible_transformations_counts, a, b

# Categorize workflows based on their complexity score
def categorize_by_complexity(score):
   if score < 40:
       return 'Simple'
   elif score < 70:
       return 'Medium'
   elif score < 100:
       return 'Complex'
   else:
       return 'Very Complex'
   
# Extract all nodes and joins from the XML file
def extract_nodes(file_path):
   tree = ET.parse(file_path)
   root = tree.getroot()
   join_nodes = []  # Store join node information
   all_nodes = []   # Store all connection node information
   # Iterate over Connection elements to find joins and all connections
   for connection in root.findall('.//Connection'):
       origin = connection.find('Origin')
       destination = connection.find('Destination')
       if origin is not None:
           origin_tool_id = origin.attrib.get('ToolID')
           origin_connection = origin.attrib.get('Connection')
           destination_tool_id = destination.attrib.get('ToolID') if destination is not None else None
           destination_connection = destination.attrib.get('Connection') if destination is not None else None
           # Identify if the origin connection is 'Left', 'Right', or 'Join'
           if origin_connection in ['Left', 'Right', 'Join']:
               join_nodes.append({
                   'Connection_Tag': connection.attrib,
                   'Origin_ToolID': origin_tool_id,
                   'Origin_Connection': origin_connection,
                   'Destination_ToolID': destination_tool_id,
                   'Destination_Connection': destination_connection
               })
           # Store all connections
           all_nodes.append({
               'Connection_Tag': connection.attrib,
               'Origin_ToolID': origin_tool_id,
               'Origin_Connection': origin_connection,
               'Destination_ToolID': destination_tool_id,
               'Destination_Connection': destination_connection
           })
   return join_nodes, all_nodes

# Process join information and categorize join types
def get_join_info(joins, nodes):
   visited = set()
   join_info = []
   for join_node in joins:
       join_type=""
       join_nodes = []
       join_node_id = (join_node['Origin_ToolID'], join_node['Connection_Tag'].get('name'))
       if join_node_id not in visited:
           visited.add(join_node_id)
           join_nodes.append(join_node)
           if 'name' in join_node['Connection_Tag']:
               for other_join in joins:
                   other_join_id = (other_join['Origin_ToolID'], other_join['Connection_Tag'].get('name'))
                   if other_join_id not in visited and other_join['Origin_ToolID'] == join_node['Origin_ToolID']:
                       join_nodes.append(other_join)
                       visited.add(other_join_id)
       if join_nodes and join_nodes[0]['Origin_ToolID'] not in visited:
           # Determine join type based on number of nodes
           if len(join_nodes) == 3:
               join_type = "Full Outer Join"
           elif len(join_nodes) == 2:
               join_type = "Left Outer Join" if join_nodes[0]['Origin_Connection'] == 'Left' else "Right Outer Join"
           elif len(join_nodes) == 1:
                if join_nodes[0]['Origin_Connection'] == 'Join':
                    join_type = 'Inner Join'
                elif join_nodes[0]['Origin_Connection'] == 'Right':
                    join_type = 'Right Unjoin'
                elif join_nodes[0]['Origin_Connection'] == 'Left':
                    join_type = 'Left Unjoin'
           # Add the join information
           join_info.append({
               "Join_Type": join_type,
               "Joining_Node": join_nodes[0]['Origin_ToolID'],
               "Nodes": [node['Origin_ToolID'] for node in nodes if node['Destination_ToolID'] == join_nodes[0]['Origin_ToolID']]
           })
   return join_info

def extract_io_info(files, target_folder):
    """
    Extract all inputs (including duplicates) and unique outputs for each workflow file based on XML elements.

    Args:
        files (list): List of workflow file names.
        target_folder (str): Directory containing the workflow files.

    Returns:
        dict: A dictionary with inputs (duplicates allowed) and unique outputs for each workflow.
    """
    io_info = {}

    for file in files:
        file_path = os.path.join(target_folder, os.path.basename(file))
        if os.path.isfile(file_path) and file.endswith((".xml", ".yxmd")):
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()

                inputs = []  # Collect all inputs, including duplicates
                outputs = set()  # Collect unique outputs

                # Loop through each node in the XML file
                for node in root.findall(".//Node"):
                    # Check for DbFileInput plugin for inputs
                    gui_settings = node.find(".//GuiSettings")
                    if gui_settings is not None:
                        plugin = gui_settings.get("Plugin", "")
                        if "DbFileInput" in plugin:  # Identifies file inputs
                            annotation = node.find(".//Annotation/DefaultAnnotationText")
                            if annotation is not None and annotation.text:
                                # Only take the part before the first space, strip any newlines or whitespace
                                input_name = annotation.text.split()[0].strip()
                                inputs.append(input_name)  # Add to inputs list, allowing duplicates

                        # Check for DbFileOutput plugin for outputs
                        if "DbFileOutput" in plugin:  # Identifies file outputs
                            annotation = node.find(".//Annotation/DefaultAnnotationText")
                            if annotation is not None and annotation.text:
                                outputs.add(annotation.text.strip())  # Add to outputs set (unique)

                # Add to the dictionary for this file
                io_info[file] = {
                    "Input": inputs,  # Preserve duplicates
                    "Output": list(outputs),  # Convert set to list for consistency
                }
            except ET.ParseError as e:
                print(f"Error parsing XML in file {file}: {e}")
            except Exception as e:
                print(f"An error occurred while processing file {file}: {e}")

    return io_info

def format_io_info(io_info):
    formatted_io_info = []
    
    for file, details in io_info.items():
        inputs = details['Input']
        outputs = details['Output']
        
        # Count occurrences of each input for the current workflow
        input_count_dict = {}
        for input_item in inputs:
            if input_item in input_count_dict:
                input_count_dict[input_item] += 1
            else:
                input_count_dict[input_item] = 1
        
        # Create formatted entries for each unique input
        for input_item, count in input_count_dict.items():
            formatted_entry = {
                'workflow': file,
                'input': input_item,
                'output': ', '.join(outputs),  # Join outputs into a single string
                'input_count': count
            }
            formatted_io_info.append(formatted_entry)
    
    return formatted_io_info

def save_as_csv(data, filepath):
    keys = data[0].keys() if data else ["workflow_name", "transformation_name", "count"]
    with open(filepath, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
        
def save_formatted_io_info_as_csv(formatted_io_info, filepath):
    
    # Write to the CSV file
    with open(filepath, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["workflow", "input", "output", "input_count"])
        writer.writeheader()  # Write the header
        writer.writerows(formatted_io_info)  # Write the data rows

import pandas as pd

def convert_io_info_to_dataframe(io_info_list):
    """
    Converts the provided list of dictionaries into a pandas DataFrame without numbering.

    Args:
        io_info_list (list): List of dictionaries with keys: workflow, input, output, and input_count.

    Returns:
        pd.DataFrame: A DataFrame summarizing the input/output information.
    """
    # Create a DataFrame directly from the input list
    df = pd.DataFrame(io_info_list)

    # Split the 'output' column into separate rows if it contains multiple outputs
    df = df.assign(output=df['output'].str.split(',')).explode('output')

    # Remove any leading/trailing whitespace in the 'output' column
    df['output'] = df['output'].str.strip()

    # Reorganize columns for better readability
    df = df[['workflow', 'input', 'output', 'input_count']]

    # Reset the index to remove numbering
    df.reset_index(drop=True, inplace=True)

    return df

def analyze_inventory(folder_name, files):
    # Define the INPUTS directory
    inputs_dir = "INPUTS"
    
    # Create the INPUTS directory if it doesn't exist
    if not os.path.exists(inputs_dir):
        os.makedirs(inputs_dir)
    
    # Define the target folder path inside the INPUTS directory
    target_folder = os.path.join(inputs_dir, folder_name)
    
    # Check if the folder exists, if not create it
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    
    # Save the files in the target folder
    # for file in files:
    #     file_path = os.path.join(target_folder, os.path.basename(file))
    #     with open(file, 'rb') as f_src:
    #         with open(file_path, 'wb') as f_dest:
    #             f_dest.write(f_src.read())
    if 'All' in files:
        files=files_list_assess(target_folder)

    total_files = 0
    total_lines = 0
    all_transformation_counts = {}
    all_not_possible_transformations = {}
    file_specific_info = []
    overall_possible=0
    overall_not_possible=0
    overall_nodes = 0
    overall_category = ['Simple', 'Medium', 'Complex', 'Very Complex']
    overall_category_type = [0] * 4
    file_conversion = ['Fully Convertible', 'Partially']
    file_conversion_count = [0] * 2
    overall_joins = ['Left Unjoin', 'Right Unjoin', 'Inner Join', 'Left Outer Join', 'Right Outer Join', 'Full Outer Join']
    overall_joins_count = [0] * 6
    for file in files:
        lines_count = 0
        file_path = os.path.join(target_folder, os.path.basename(file))
        if os.path.isfile(file_path) and (file.endswith(".xml") or file.endswith(".txt") or file.endswith(".yxmd")):
            total_files += 1
            # Read the file and count lines of code
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                lines_count += len(lines)
                total_lines += lines_count
            # Extract connections, transformations, and join nodes
            total_nodes = count_total_nodes(file_path)
            overall_nodes = overall_nodes + total_nodes
            transformation_counts, not_possible_transformations,a,b = extract_transformations_from_xml(file_path)
            overall_possible = overall_possible + a
            overall_not_possible = overall_not_possible + b
            join_nodes, all_nodes = extract_nodes(file_path)
            join_info = get_join_info(join_nodes, all_nodes)
            for join in join_info:
                if(join['Join_Type'] == "Left Unjoin"):
                    overall_joins_count[0] = overall_joins_count[0] + 1
                elif(join['Join_Type'] == "Right Unjoin"):
                    overall_joins_count[1] = overall_joins_count[1] + 1
                elif(join['Join_Type'] == "Inner Join"):
                    overall_joins_count[2] = overall_joins_count[2] + 1
                elif(join['Join_Type'] == "Left Outer Join"):
                    overall_joins_count[3] = overall_joins_count[3] + 1
                elif(join['Join_Type'] == "Right Outer Join"):
                    overall_joins_count[4] = overall_joins_count[4] + 1
                elif(join['Join_Type'] == "Full Outer Join"):
                    overall_joins_count[5] = overall_joins_count[5] + 1
            transformation_counts['Joins'] = len(join_info)
            overall_possible = overall_possible + len(join_info)
            
            # Aggregate transformation counts and not possible transformations
            for key, value in transformation_counts.items():
                if key in all_transformation_counts:
                    all_transformation_counts[key] += value
                else:
                    all_transformation_counts[key] = value
            
            for key, value in not_possible_transformations.items():
                if key in all_not_possible_transformations:
                    all_not_possible_transformations[key] += value
                else:
                    all_not_possible_transformations[key] = value
            
            # Load complexity weights
            complexity_weights_file=os.path.join(os.getcwd(),'static','assets','analyzer','complexity_weights.json')
            complexity_weights = load_json_file(complexity_weights_file)
            # complexity_weights = load_json_file('./complexity_weights.json')

            # Calculate the complexity score
            complexity_score = calculate_complexity_score(
                transformation_counts, join_info, len(lines), complexity_weights
            )
            category = categorize_by_complexity(complexity_score)
            if(category == 'Simple'):  
                overall_category_type[0] = overall_category_type[0] + 1
            elif(category == 'Medium'):
                overall_category_type[1] = overall_category_type[1] + 1
            elif(category == 'Complex'):
                overall_category_type[2] = overall_category_type[2] + 1
            else:
                overall_category_type[3] = overall_category_type[3] + 1 

            if(len(not_possible_transformations) == 0):
                file_conversion_count[0] = file_conversion_count[0] + 1
            else:
                file_conversion_count[1] = file_conversion_count[1] + 1
            # Store file-specific information
            file_specific_info.append({
                "file": file,
                "total_nodes": total_nodes,
                "join_info": join_info,
                "complexity_score": complexity_score,
                "complexity_category": category,
                "lines_count": lines_count,
                "transformation_counts": transformation_counts,
                "not_possible_transformations": not_possible_transformations
            })

    sorted_transformations = sorted(all_transformation_counts.items(), key=lambda item: item[1], reverse=True)
    sorted_non_transformations = sorted(all_not_possible_transformations.items(), key=lambda item: item[1], reverse=True)
    total_transformations_count= overall_possible+overall_not_possible
    io_info = extract_io_info(files, target_folder)
    formatted_io_info = format_io_info(io_info)
    
    
    
     # New list to store workflow names and their transformations
    workflow_transformation_data = []

    for file in files:
        file_path = os.path.join(target_folder, os.path.basename(file))
        # Skip non-Alteryx files
        if not (file.endswith(".xml") or file.endswith(".txt") or file.endswith(".yxmd")):
            continue
        
        # Extract transformations from the file
        transformation_counts, not_possible_transformations, a, b = extract_transformations_from_xml(file_path)
        
        # Add transformations for the current workflow to the data
        for transformation, count in transformation_counts.items():
            workflow_transformation_data.append({
                "workflow_name": file,
                "transformation_name": transformation,
                "count": count
            })

    # Save the workflow transformation data as a CSV file
    csv_file_path = os.path.join(os.getcwd(), "workflow_transformations.csv")
    save_as_csv(workflow_transformation_data, csv_file_path)
    
    io_info_csv_file_path = os.path.join(os.getcwd(), "io_info.csv")
    save_as_csv(formatted_io_info, io_info_csv_file_path)
    io_info_df = convert_io_info_to_dataframe(formatted_io_info)
    
    return {
        "total_files": total_files,
        "total_lines": total_lines,
        "total_nodes_count": overall_nodes,
        "sorted_transformations": sorted_transformations,
        "sorted_non_transformations": sorted_non_transformations,
        "total_transformations_count": total_transformations_count,
        "overall_transformations_count": overall_possible,
        "overall_non_transformations_count": overall_not_possible,
        "overall_category": overall_category,
        "overall_category_type": overall_category_type,
        "file_conversion": file_conversion,
        "file_conversion_count": file_conversion_count,
        "overall_joins": overall_joins,
        "overall_joins_count": overall_joins_count,
        "file_specific_info": file_specific_info,
        "io_info": io_info_df,
        "f_io":formatted_io_info
    }

if __name__ == "__main__":
    result = analyze_inventory("C:\\Users\\10839330\\OneDrive - LTIMindtree\\Desktop\\Ollama_Agents\\INPUTS\\CUST1_SPC",["All"])

    print(result)