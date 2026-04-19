import os
import sys
import subprocess
import tempfile

def main():
    if len(sys.argv) < 3:
        print("Usage: python ftap_to_s2ml_converter.py <input.ftp> <output.sbe>")
        sys.exit(1)
        
    input_ftp = sys.argv[1]
    output_sbe = sys.argv[2]
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ftap_to_openpsa = os.path.join(script_dir, "ftap_to_openpsa_converter.py")
    openpsa_to_s2ml = os.path.join(script_dir, "openpsa_to_s2ml_converter.py")
    
    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tmp:
        tmp_xml = tmp.name
        
    try:
        # Step 1: FTAP -> OpenPSA XML
        subprocess.run([sys.executable, ftap_to_openpsa, input_ftp, tmp_xml], check=True)
        
        # Step 2: OpenPSA XML -> S2ML+SBE
        subprocess.run([sys.executable, openpsa_to_s2ml, "-i", tmp_xml, "-o", output_sbe], check=True)
        
        print(f"Successfully converted {input_ftp} to {output_sbe}")
    finally:
        if os.path.exists(tmp_xml):
            os.remove(tmp_xml)

if __name__ == "__main__":
    main()
