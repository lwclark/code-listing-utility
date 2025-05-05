from pathlib import Path
try:
    from gitignore_parser import parse_gitignore
    HAS_GITIGNORE_PARSER = True
except ImportError:
    HAS_GITIGNORE_PARSER = False

def basic_gitignore_parser(gitignore_path: Path):
    if not gitignore_path.exists():
        return lambda x: False
    patterns = []
    with open(gitignore_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                patterns.append(line)
    def matches(path):
        rel_path = str(Path(path).relative_to(gitignore_path.parent))
        return any(p in rel_path or rel_path.startswith(p + "/") for p in patterns)
    return matches

def get_gitignore_matcher(root_path: Path):
    gitignore_path = root_path / ".gitignore"
    if HAS_GITIGNORE_PARSER and gitignore_path.exists():
        return parse_gitignore(gitignore_path)
    return basic_gitignore_parser(gitignore_path)