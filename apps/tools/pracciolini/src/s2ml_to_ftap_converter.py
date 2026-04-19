import os
import sys
import re

def convert_s2ml_to_ftap(input_path, output_path):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    gates = []
    basic_events = []
    
    # Parse gates
    # gate <name> = <formula>;
    gate_pattern = re.compile(r"gate\s+(\w+)\s*=\s*([^;]+);", re.MULTILINE)
    for match in gate_pattern.finditer(content):
        name = match.group(1)
        formula = match.group(2).strip()
        
        # Determine operator
        op = "*"
        if " or " in formula:
            op = "+"
        elif " and " in formula:
            op = "*"
        elif formula.startswith("atleast"):
            # Simplified handling for atleast: convert to OR if multiple, or AND if it's atleast N of N
            # But FTAP doesn't support atleast. We'll just mark it.
            # For now, let's just use OR as a fallback or AND.
            op = "+" 
        
        # Extract children
        # This is a bit naive if it's nested, but works for flat models
        children_str = formula
        if op == "+":
            children = [c.strip() for c in children_str.split(" or ")]
        elif op == "*":
            children = [c.strip() for c in children_str.split(" and ")]
        else:
            children = [children_str]
            
        processed_children = []
        for child in children:
            negated = False
            if child.startswith("not "):
                negated = True
                child = child[4:].strip()
            
            if negated:
                processed_children.append(f"-{child}")
            else:
                processed_children.append(child)
                
        gates.append(f"{name} {op} {' '.join(processed_children)}")

    # Parse basic events
    # basic-event <name> = <prob>;
    be_pattern = re.compile(r"basic-event\s+(\w+)\s*=\s*([^;]+);", re.MULTILINE)
    for match in be_pattern.finditer(content):
        name = match.group(1)
        prob = match.group(2).strip()
        basic_events.append(f"{prob} {name}")

    # Write FTAP file
    lines = []
    lines.extend(gates)
    lines.append("ENDTREE")
    
    if gates:
        top_event = gates[0].split()[0]
        lines.append(f"PROCESS {top_event}")
        
    lines.append("import")
    lines.extend(basic_events)
    lines.append("LIMIT 1E-300")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python s2ml_to_ftap_converter.py <input.sbe> <output.ftp>")
        sys.exit(1)
    convert_s2ml_to_ftap(sys.argv[1], sys.argv[2])
