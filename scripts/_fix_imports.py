"""Fix all bare internal imports in backend/ by prepending backend. prefix.

Walk every .py file, parse it with ast, and rewrite any from-import whose
first-level module is an internal VELYNX subpackage (under backend/) but
lacks the backend. prefix.
"""
import ast
import os
import re

BACKEND = os.path.join(os.path.dirname(__file__), "backend")

# Get all subpackage names = first-level dirs inside backend/ that are actual
# Python packages (contain __init__.py or are importable dirs).
INTERNAL_PKGS: set[str] = set()
for name in os.listdir(BACKEND):
    d = os.path.join(BACKEND, name)
    if os.path.isdir(d) and not name.startswith("_") and not name.startswith("."):
        if os.path.isfile(os.path.join(d, "__init__.py")):
            INTERNAL_PKGS.add(name)
        else:
            # Maybe it's still importable even without __init__ (namespace package)?
            INTERNAL_PKGS.add(name)

# Some dirs aren't subpackages — exclude them.
EXCLUDE = {"__pycache__", ".git", ".github"}
INTERNAL_PKGS -= EXCLUDE

print(f"Internal subpackages: {sorted(INTERNAL_PKGS)}")

# Pattern: from <internal_pkg>.<rest> import ...  or  from <internal_pkg> import ...
# or import <internal_pkg>.<rest>
FROM_RE = re.compile(
    r"^(from\s+)(" + "|".join(re.escape(p) for p in sorted(INTERNAL_PKGS, key=len, reverse=True)) + r")(\.|\s+import\s)",
    re.MULTILINE,
)
IMPORT_RE = re.compile(
    r"^(import\s+)(" + "|".join(re.escape(p) for p in sorted(INTERNAL_PKGS, key=len, reverse=True)) + r")\.(?=\w)",
    re.MULTILINE,
)

fixed_count = 0
file_count = 0
for dirpath, _, filenames in os.walk(BACKEND):
    for f in filenames:
        if not f.endswith(".py"):
            continue
        filepath = os.path.join(dirpath, f)
        with open(filepath, encoding="utf-8") as fh:
            content = fh.read()

        new_content = FROM_RE.sub(r"\1backend.\2\3", content)
        new_content = IMPORT_RE.sub(r"\1backend.\2.", new_content)

        if new_content != content:
            with open(filepath, "w", encoding="utf-8") as fh:
                fh.write(new_content)
            file_count += 1
            # Count the actual replacements
            from_fixes = FROM_RE.findall(content)
            import_fixes = IMPORT_RE.findall(content)
            fixed_count += len(from_fixes) + len(import_fixes)
            print(f"  Fixed {filepath}")

print(f"\nDone! Fixed {fixed_count} imports across {file_count} files.")
