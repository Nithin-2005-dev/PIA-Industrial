import ast
import os
from pathlib import Path

def generate_validation_framework():
    backend_dir = Path(os.path.dirname(os.path.dirname(__file__)))
    evaluators_dir = backend_dir / "app" / "measurement" / "evaluators"
    docs_dir = backend_dir / "docs"
    docs_dir.mkdir(exist_ok=True)
    
    output_file = docs_dir / "validation_framework.md"
    
    with open(output_file, "w", encoding="utf-8") as out:
        out.write("# PIA Validation Framework\n\n")
        out.write("This document is auto-generated from evaluator metadata and docstrings.\n\n")
        
        for py_file in sorted(evaluators_dir.glob("*.py")):
            if py_file.name == "__init__.py":
                continue
                
            with open(py_file, "r", encoding="utf-8") as f:
                code = f.read()
                
            tree = ast.parse(code)
            docstring = ast.get_docstring(tree)
            if docstring:
                out.write(f"## {py_file.stem.replace('_', ' ').title()}\n\n")
                
                # Split docstring into key-value pairs based on headers (Purpose:, Mathematical Basis:, etc.)
                lines = docstring.split("\n")
                current_header = None
                content = []
                
                for line in lines:
                    if line.strip().endswith(":") and " " not in line.strip()[:-1]:
                        if current_header:
                            out.write(f"**{current_header}**\n{' '.join(content).strip()}\n\n")
                        current_header = line.strip()[:-1]
                        content = []
                    elif current_header:
                        content.append(line.strip())
                        
                if current_header:
                    out.write(f"**{current_header}**\n{' '.join(content).strip()}\n\n")
                
if __name__ == "__main__":
    generate_validation_framework()
    print("Generated docs/validation_framework.md")
