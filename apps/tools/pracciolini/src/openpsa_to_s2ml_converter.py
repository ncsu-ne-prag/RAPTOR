import os
from lxml import etree


# Gate operator tags that XFTA's S2ML+SBE cannot evaluate correctly for
# probabilistic basic events. Models containing these are skipped.
_INCOMPATIBLE_OPS = frozenset({"not", "xor"})


def _has_incompatible_ops(element: etree._Element) -> bool:
    """Return True if any descendant gate operator is not supported by XFTA S2ML+SBE."""
    if element.tag in _INCOMPATIBLE_OPS:
        return True
    return any(_has_incompatible_ops(child) for child in element)


def _check_incompatible(root: etree._Element) -> list:
    """Return a list of incompatible operator tags found in all gate bodies."""
    found = set()
    for fault_tree in root.iter("define-fault-tree"):
        for gate_el in fault_tree:
            if gate_el.tag != "define-gate":
                continue
            for body in gate_el:
                for desc in body.iter():
                    if desc.tag in _INCOMPATIBLE_OPS:
                        found.add(desc.tag)
    return sorted(found)


def get_top_event_name(input_path: str) -> str:
    """Return the name of the top event (first defined gate) in an OpenPSA XML file."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    with open(input_path, "rb") as f:
        root = etree.parse(f).getroot()
    for fault_tree in root.iter("define-fault-tree"):
        for child in fault_tree:
            if child.tag == "define-gate":
                return child.get("name")
    raise ValueError(f"No gate found in fault tree in: {input_path}")


def _formula_from_element(element: etree._Element) -> str:
    """
    Recursively convert an OpenPSA gate body element to an S2ML+SBE boolean formula string.

    Supported operators:
      <and>      -> operand1 and operand2 and ...
      <or>       -> operand1 or operand2 or ...
      <not>      -> not operand
      <atleast k="N"> -> atleast N (op1, op2, ...)
      <gate name="X"> -> X
      <basic-event name="X"> -> X
      <house-event name="X"> -> X
    """
    tag = element.tag

    if tag == "and":
        operands = [_formula_from_element(child) for child in element]
        return " and ".join(operands)

    if tag == "or":
        operands = [_formula_from_element(child) for child in element]
        return " or ".join(operands)

    if tag == "not":
        children = list(element)
        return f"not {_formula_from_element(children[0])}"

    if tag == "atleast":
        k = element.get("k", element.get("min", "2"))
        operands = [_formula_from_element(child) for child in element]
        return f"atleast {k} ({', '.join(operands)})"

    if tag in ("gate", "basic-event", "house-event"):
        return element.get("name")

    raise ValueError(f"Unsupported OpenPSA gate operator: <{tag}>")


def convert_openpsa_to_s2ml_sbe(input_path: str, output_path: str) -> None:
    """
    Convert a SCRAM OpenPSA MEF XML file to S2ML+SBE (textual) format accepted by XFTA.

    S2ML+SBE output structure:
      gate <name> = <boolean-formula>;
      ...
      basic-event <name> = <probability-value>;
      ...

    Supported probability models:
      <float value="V"/>           -> V  (constant probability)
      <exponential mean="M"/>      -> exponential(1/M)  (rate = 1/mean)
      <exponential lambda="L"/>    -> exponential(L)
      <exponential>  with <parameter name="lambda"/>  -> exponential(lambda)

    Args:
        input_path:  Path to the source SCRAM OpenPSA MEF XML file.
        output_path: Path where the converted S2ML+SBE text file will be written.

    Raises:
        FileNotFoundError: If input_path does not exist.
        ValueError: If the file does not have the expected <opsa-mef> root element.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, "rb") as f:
        tree = etree.parse(f)

    root = tree.getroot()
    if root.tag != "opsa-mef":
        raise ValueError(
            f"Expected root element <opsa-mef>, got <{root.tag}>. "
            "This file may not be a SCRAM OpenPSA MEF document."
        )

    incompatible = _check_incompatible(root)
    if incompatible:
        raise ValueError(
            f"Model contains gate operator(s) incompatible with XFTA S2ML+SBE: "
            f"{', '.join(f'<{t}>' for t in incompatible)}. "
            "XFTA cannot evaluate probabilistic NOT or XOR. Skipping conversion."
        )

    lines = []

    # --- Gates ---
    for fault_tree in root.iter("define-fault-tree"):
        for gate_el in fault_tree:
            if gate_el.tag != "define-gate":
                continue
            name = gate_el.get("name")
            body = list(gate_el)
            if not body:
                raise ValueError(f"Gate '{name}' has no body element.")
            formula = _formula_from_element(body[0])
            lines.append(f"gate {name} = {formula};")

    lines.append("")  # blank separator

    # --- Basic events ---
    for model_data in root.iter("model-data"):
        for be_el in model_data:
            if be_el.tag != "define-basic-event":
                continue
            name = be_el.get("name")
            prob_expr = _probability_expression(be_el)
            lines.append(f"basic-event {name} = {prob_expr};")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def _probability_expression(be_element: etree._Element) -> str:
    """
    Extract the probability expression from a <define-basic-event> element and
    return the corresponding S2ML+SBE expression string.
    """
    children = list(be_element)
    if not children:
        raise ValueError(
            f"<define-basic-event name='{be_element.get('name')}'> has no probability model."
        )

    model = children[0]
    tag = model.tag

    if tag == "float":
        return model.get("value")

    if tag == "exponential":
        # Check for inline lambda/mean attributes first
        if model.get("lambda"):
            return f"exponential({model.get('lambda')})"
        if model.get("mean"):
            mean = float(model.get("mean"))
            rate = 1.0 / mean
            return f"exponential({rate:.6g})"
        # Otherwise look for a child <parameter name="lambda"> element
        params = {p.get("name"): p.get("value", p.get("name")) for p in model}
        if "lambda" in params:
            return f"exponential({params['lambda']})"
        raise ValueError(
            f"Cannot determine rate for <exponential> in event '{be_element.get('name')}'."
        )

    raise ValueError(
        f"Unsupported probability model <{tag}> in event '{be_element.get('name')}'."
    )


def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Convert SCRAM OpenPSA MEF XML files to XFTA S2ML+SBE format."
    )
    parser.add_argument("-i", "--input", required=True, help="Input SCRAM OpenPSA MEF XML file")
    parser.add_argument("-o", "--output", help="Output S2ML+SBE file path (.sbe)")
    parser.add_argument(
        "--get-top-event",
        action="store_true",
        help="Print the top event name to stdout and exit (no conversion performed)",
    )

    args = parser.parse_args()

    if args.get_top_event:
        try:
            print(get_top_event_name(args.input))
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    if not args.output:
        print("Error: -o/--output is required for conversion.", file=sys.stderr)
        sys.exit(1)

    try:
        convert_openpsa_to_s2ml_sbe(args.input, args.output)
        print(f"Conversion successful: {args.input} -> {args.output}")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
