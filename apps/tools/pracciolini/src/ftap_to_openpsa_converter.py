import os
import sys
import re
from lxml import etree

def convert_ftap_to_openpsa(input_path, output_path):
    with open(input_path, 'r') as f:
        lines = f.readlines()

    gates = {}
    basic_events = {}
    top_events = []
    
    section = None
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith(';'):
            continue
            
        upper_line = line.upper()
        
        if upper_line.startswith('FAULT TREE'):
            section = 'GATES'
            continue
        elif upper_line.startswith('ENDTREE'):
            section = None
            continue
        elif upper_line.startswith('PROCESS'):
            section = 'PROCESS'
            parts = line.split()
            if len(parts) > 1:
                top_events.extend(parts[1:])
            continue
        elif upper_line.startswith('IMPORT'):
            section = 'IMPORT'
            continue
        elif upper_line.startswith('LIMIT') or upper_line.startswith('*XEQ'):
            section = None
            continue
            
        if section == 'GATES':
            # Format: NAME OP CHILD1 CHILD2 ...
            # OP: + (OR), * (AND)
            parts = line.split()
            if len(parts) < 3:
                continue
            
            gate_name = parts[0]
            op_char = parts[1]
            children = parts[2:]
            
            op = 'or' if op_char == '+' else 'and'
            
            processed_children = []
            for child in children:
                negated = False
                if child.startswith('-') or child.startswith('/'):
                    negated = True
                    child = child[1:]
                processed_children.append({'name': child, 'negated': negated})
                
            gates[gate_name] = {'op': op, 'children': processed_children}
            
        elif section == 'PROCESS':
            parts = line.split()
            top_events.extend(parts)
            
        elif section == 'IMPORT':
            # Format: PROB NAME
            parts = line.split()
            if len(parts) >= 2:
                try:
                    prob = float(parts[0])
                    name = parts[1]
                    basic_events[name] = prob
                except ValueError:
                    # Maybe it's NAME PROB? (Some formats differ)
                    try:
                        prob = float(parts[1])
                        name = parts[0]
                        basic_events[name] = prob
                    except ValueError:
                        continue

    # Build OpenPSA XML
    root = etree.Element('opsa-mef')
    
    # Define Fault Tree
    ft = etree.SubElement(root, 'define-fault-tree', name='FTREX_Import')
    
    # We need to distinguish between gates and basic events
    all_gate_names = set(gates.keys())
    
    for gate_name, info in gates.items():
        gate_el = etree.SubElement(ft, 'define-gate', name=gate_name)
        op_el = etree.SubElement(gate_el, info['op'])
        
        for child in info['children']:
            parent_el = op_el
            if child['negated']:
                parent_el = etree.SubElement(op_el, 'not')
            
            if child['name'] in all_gate_names:
                etree.SubElement(parent_el, 'gate', name=child['name'])
            else:
                etree.SubElement(parent_el, 'basic-event', name=child['name'])
                if child['name'] not in basic_events:
                    basic_events[child['name']] = 0.0 # Default
                    
    # Define Model Data (Basic Events)
    model_data = etree.SubElement(root, 'model-data')
    for be_name, prob in basic_events.items():
        be_el = etree.SubElement(model_data, 'define-basic-event', name=be_name)
        etree.SubElement(be_el, 'float', value=str(prob))
        
    tree = etree.ElementTree(root)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    tree.write(output_path, encoding='utf-8', xml_declaration=True, pretty_print=True)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python ftap_to_openpsa_converter.py <input.ftp> <output.xml>")
        sys.exit(1)
    convert_ftap_to_openpsa(sys.argv[1], sys.argv[2])
