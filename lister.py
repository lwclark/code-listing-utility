import os
from pathlib import Path
import pyperclip
from .config import ProjectConfig, FRONTEND_EXTS, BACKEND_EXTS, CONFIG_EXTS
from .gitignore import get_gitignore_matcher
from .summarizer import summarize_file

def generate_code_listing(root_path: str, max_depth: int = None, extra_exclude_dirs: set = None,
                        extra_exclude_files: set = None) -> tuple[str, str | None]:
    config = ProjectConfig(root_path, extra_exclude_dirs=extra_exclude_dirs,
                         extra_exclude_files=extra_exclude_files)
    root = config.root
    
    if not root.exists():
        return "", "Error: Directory does not exist."

    summary = [f"Project Root: {root.name}",
               "Overview: Full-stack app with FastAPI backend and React frontend"]
    config_summary = ["\nConfiguration Files:"]
    file_counts = {"frontend": {}, "backend": {}}
    total_lines = {"frontend": 0, "backend": 0}
    ignore = get_gitignore_matcher(root)
    code_listings = {"frontend": [], "backend": []}

    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        current_dir = Path(dirpath).name
        if current_dir in config.exclude_dirs:
            dirnames.clear()
            continue

        rel_depth = len(Path(dirpath).relative_to(root).parts)
        if max_depth is not None and rel_depth > max_depth:
            continue

        dirnames[:] = [d for d in dirnames if not ignore(os.path.join(dirpath, d))]
        valid_files = [
            f for f in filenames
            if not ignore(os.path.join(dirpath, f))
            and Path(f).suffix.lower() in (FRONTEND_EXTS | BACKEND_EXTS | CONFIG_EXTS)
            and f not in config.exclude_files
        ]

        if valid_files:
            rel_path = Path(dirpath).relative_to(root)
            is_frontend = config.is_frontend(rel_path)
            section = "frontend" if is_frontend else "backend"
            file_summaries = []
            
            for fname in valid_files:
                ext = Path(fname).suffix.lower() or ".no_ext"
                file_path = Path(dirpath) / fname
                file_counts[section][ext] = file_counts[section].get(ext, 0) + 1
                
                file_summary = summarize_file(file_path, is_frontend)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        total_lines[section] += len(content.splitlines())
                        code_listings[section].append(f"### {rel_path}/{fname}\n```\n{content}\n```")
                except Exception as e:
                    code_listings[section].append(f"### {rel_path}/{fname}\nError reading file: {str(e)}")
                
                if file_summary:
                    if ext in CONFIG_EXTS and "config" in fname.lower():
                        config_summary.append(f"  - {rel_path}/{fname} - Lines: {len(open(file_path).readlines())}")
                    else:
                        file_summaries.append(file_summary)
            
            if file_summaries:
                indent = "  " * rel_depth
                summary.append(f"{indent}- /{rel_path} ({len(file_summaries)} files)")
                summary.extend(file_summaries)

    if len(config_summary) > 1:
        summary.extend(config_summary)
    
    for section in ["frontend", "backend"]:
        summary.append(f"\n{section.capitalize()} File Types:")
        for ext, count in sorted(file_counts[section].items()):
            summary.append(f"  - {ext}: {count} files")
        summary.append(f"Total {section.capitalize()} Lines: {total_lines[section]}")

    # Write code listings
    for section, listing in code_listings.items():
        if listing:
            output_file = root / f"{section}_code.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"{section.capitalize()} Code Listings for {root.name}\n\n")
                f.write("\n\n".join(listing))
            print(f"Generated {output_file}")

    return "\n".join(summary), None