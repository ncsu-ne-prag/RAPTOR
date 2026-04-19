import os
import sys
from lxml import etree

def get_top_event_name(root):
    for fault_tree in root.iter("define-fault-tree"):
        for child in fault_tree:
            if child.tag == "define-gate":
                return child.get("name")
    return None

def convert_openpsa_to_ftap(input_path, output_path):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, "rb") as f:
        tree = etree.parse(f)
    root = tree.getroot()

    lines = ["Fault tree"]
    
    # --- Gates ---
    for fault_tree in root.iter("define-fault-tree"):
        for gate_el in fault_tree:
            if gate_el.tag != "define-gate":
                continue
            gate_name = gate_el.get("name")
            body = list(gate_el)
            if not body:
                continue
            
            formula_el = body[0]
            tag = formula_el.tag
            
            op = "+" if tag == "or" else "*"
            if tag not in ("or", "and"):
                # Handle other operators if needed, or skip
                continue
                
            children = []
            for child in formula_el:
                negated = False
                if child.tag == "not":
                    negated = True
                    child = child[0]
                
                name = child.get("name")
                if negated:
                    children.append(f"-{name}")
                else:
                    children.append(name)
            
            lines.append(f"{gate_name} {op} {' '.join(children)}")

    lines.append("ENDTREE")
    
    top_event = get_top_event_name(root)
    if top_event:
        lines.append(f"PROCESS {top_event}")
        
    lines.append("IMPORT")
    
    # --- Basic Events ---
    for model_data in root.iter("model-data"):
        for be_el in model_data:
            if be_el.tag != "define-basic-event":
                continue
            name = be_el.get("name")
            
            # Get probability
            prob = "0.0"
            for child in be_el:
                if child.tag == "float":
                    prob = child.get("value")
                    break
                elif child.tag == "exponential":
                    # For simplicity, we might just use a placeholder or calculate it
                    # But ARALIA dataset usually uses constant probabilities
                    prob = "0.0"
            
            lines.append(f"{prob} {name}")
            
    lines.append("LIMIT 0.00E-00")
    lines.append("*XEQ")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python openpsa_to_ftap_converter.py <input.xml> <output.ftp>")
        sys.exit(1)
    convert_openpsa_to_ftap(sys.argv[1], sys.argv[2])
