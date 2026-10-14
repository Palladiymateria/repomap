import argparse
from pathlib import Path
import sys
from .core import inventory, tree, bundle


def positive(value):
    result = int(value)
    if result <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Map a project or bundle its text files for AI. Runs locally; no uploads.")
    parser.add_argument("folder", nargs="?", default=".")
    parser.add_argument("--bundle", action="store_true", help="Generate Markdown containing selected text files")
    parser.add_argument("--include", action="append", default=[], metavar="GLOB", help="Include matching files (repeatable; quote patterns)")
    parser.add_argument("--exclude", action="append", default=[], metavar="GLOB", help="Exclude matching files or directories (repeatable)")
    parser.add_argument("--depth", type=positive, default=5, help="Tree display depth; does not limit bundled files (default: 5)")
    parser.add_argument("--max-file-kb", type=positive, default=128, help="Maximum source bytes per file in KiB (default: 128)")
    parser.add_argument("--max-total-kb", type=positive, default=1024, help="Maximum total source bytes in KiB (default: 1024)")
    parser.add_argument("-o", "--output", type=Path, help="Save to a new UTF-8 file; existing files are never overwritten")
    args = parser.parse_args(argv)
    try:
        root, files, git_filter = inventory(args.folder, args.include, args.exclude, [args.output] if args.output else [])
        if args.bundle:
            content, included, skipped = bundle(root, files, args.max_file_kb * 1024, args.max_total_kb * 1024, args.depth)
            summary = f"{included} files bundled; {len(skipped)} contents skipped"
        else:
            content = tree(files, root.name, args.depth) + "\n"
            summary = f"{len(files)} files selected"
        if args.output:
            with args.output.open("x", encoding="utf-8") as target:
                target.write(content)
        else:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
            print(content, end="")
        print(f"RepoMap: {summary}. Git ignore filtering: {'on' if git_filter else 'off (not a Git root or Git unavailable)' }.", file=sys.stderr)
        return 0
    except (ValueError, OSError) as error:
        print(f"RepoMap: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
