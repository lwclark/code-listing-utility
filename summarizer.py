import ast
import re
from pathlib import Path
from .config import FRONTEND_EXTS, BACKEND_EXTS, CONFIG_EXTS

def summarize_file(file_path: Path, is_frontend: bool) -> str | None:
    ext = file_path.suffix.lower()
    summary = [f"File: {file_path.name}"]
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.splitlines()
            line_count = len(lines)
        
        if line_count == 0 and file_path.name == "__init__.py":
            return None

        if ext in BACKEND_EXTS:
            return summarize_backend_file(file_path, content, line_count)
        elif ext in FRONTEND_EXTS:
            return summarize_frontend_file(file_path, content, line_count)
        elif ext in CONFIG_EXTS:
            summary.append("  - Purpose: Configuration file")
            summary.append(f"  - Lines: {line_count}")
            return "\n".join(summary)
        return None
    except Exception as e:
        summary.append(f"  - Error reading file: {str(e)}")
        return "\n".join(summary)

def summarize_backend_file(file_path: Path, content: str, line_count: int) -> str | None:
    summary = [f"File: {file_path.name}"]
    try:
        tree = ast.parse(content)
        funcs = []
        classes = []
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                args = [a.arg for a in node.args.args]
                doc = ast.get_docstring(node) or f"Purpose inferred: {node.name.replace('_', ' ')}"
                funcs.append(f"  - Function: {node.name}({', '.join(args)}) - {doc.splitlines()[0]}")
            elif isinstance(node, ast.ClassDef):
                doc = ast.get_docstring(node) or "No docstring"
                classes.append(f"  - Class: {node.name} - {doc.splitlines()[0]}")
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.update([n.name.split('.')[0] for n in node.names])
        
        summary.extend(classes)
        summary.extend(funcs)
        if imports:
            summary.append(f"  - Key Imports: {', '.join(sorted(imports)[:5])}{'...' if len(imports) > 5 else ''}")
        
        if file_path.name == "main.py":
            summary.append("  - Purpose: Application entry point")
        elif re.search(r"@app\.(get|post|put|delete)", content):
            summary.append("  - Purpose: FastAPI route")
        elif not funcs and not classes and line_count < 5:
            return None
        elif not funcs and not classes:
            summary.append("  - Purpose: Utility or config")
        
        summary.append(f"  - Lines: {line_count}")
        return "\n".join(summary)
    except SyntaxError:
        summary.append("  - Syntax error; unable to parse.")
        summary.append(f"  - Lines: {line_count}")
        return "\n".join(summary)

def summarize_frontend_file(file_path: Path, content: str, line_count: int) -> str | None:
    summary = [f"File: {file_path.name}"]
    ext = file_path.suffix.lower()
    
    if file_path.name in ["main.jsx", "main.js"]:
        summary.append("  - Purpose: Frontend entry point")
        if "ReactDOM" in content:
            summary.append("  - Initializes: React application")
    else:
        func_matches = re.findall(r"(?:function|const|let|var)\s+(\w+)\s*\(([^)]*)\)\s*(?:=>|\{)", content)
        for name, args in func_matches:
            comment = re.search(r"/\*\*.*?\*/|//.*$", content[:content.index(name)], re.DOTALL)
            doc = comment.group().strip() if comment else f"Purpose inferred: {name.replace('_', ' ')}"
            summary.append(f"  - Function: {name}({args.strip()}) - {doc}")
        
        class_matches = re.findall(r"class\s+(\w+)", content)
        for name in class_matches:
            summary.append(f"  - Class: {name} - Component or utility class")
        
        if ext in [".jsx", ".tsx"] and "return (" in content:
            summary.append("  - Purpose: React component")
        elif not func_matches and not class_matches and line_count < 5:
            return None
        elif not func_matches and not class_matches:
            summary.append("  - Purpose: Utility or script")
    
    summary.append(f"  - Lines: {line_count}")
    return "\n".join(summary)