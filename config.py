from pathlib import Path

# Default excluded directories
BASE_EXCLUDE_DIRS = {
    "node_modules", "dist", "build", "__pycache__", "venv", ".venv", "lib", "vendor", ".git", "archive"
}

# File extensions
FRONTEND_EXTS = {".js", ".jsx", ".ts", ".tsx"}
BACKEND_EXTS = {".py"}
CONFIG_EXTS = {".json", ".js"}  # For package.json, vite.config.js, etc.

# Project structure
DEFAULT_FRONTEND_DIRS = {"frontend", "client", "src"}
DEFAULT_BACKEND_DIRS = {"backend", "server", "api"}

class ProjectConfig:
    def __init__(self, root_path: str, frontend_dirs: set = None, backend_dirs: set = None,
                 extra_exclude_dirs: set = None, extra_exclude_files: set = None):
        self.root = Path(root_path).resolve()
        self.frontend_dirs = frontend_dirs or DEFAULT_FRONTEND_DIRS
        self.backend_dirs = backend_dirs or DEFAULT_BACKEND_DIRS
        self.exclude_dirs = BASE_EXCLUDE_DIRS | (extra_exclude_dirs or set())
        self.exclude_files = extra_exclude_files or set()

    def is_frontend(self, path: Path) -> bool:
        """Check if a path belongs to frontend."""
        return any(d in path.parts for d in self.frontend_dirs)

    def is_backend(self, path: Path) -> bool:
        """Check if a path belongs to backend."""
        return any(d in path.parts for d in self.backend_dirs)