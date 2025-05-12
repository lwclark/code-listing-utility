#python -m code_lister.cli --path ..\tellshirley\

import argparse
import pyperclip
from .lister import generate_code_listing

def main():
    parser = argparse.ArgumentParser(description="Summarize a codebase for Grok context.")
    parser.add_argument("--path", default=".", help="Path to project directory")
    parser.add_argument("--depth", type=int, help="Max directory depth")
    parser.add_argument("--exclude-dirs", nargs="*", default=[], help="Additional directories to exclude")
    parser.add_argument("--exclude-files", nargs="*", default=[], help="Additional files to exclude")
    parser.add_argument("--no-clipboard", action="store_true", help="Print output instead of copying")
    args = parser.parse_args()

    summary, error = generate_code_listing(
        args.path,
        max_depth=args.depth,
        extra_exclude_dirs=set(args.exclude_dirs),
        extra_exclude_files=set(args.exclude_files)
    )
    
    if error:
        print(error)
        return

    if args.no_clipboard:
        print(summary)
    else:
        try:
            pyperclip.copy(summary)
            print("Summary copied to clipboard!")
            print(summary)
        except pyperclip.PyperclipException:
            print("Clipboard functionality unavailable. Output:\n")
            print(summary)

if __name__ == "__main__":
    main()