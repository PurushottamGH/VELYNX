import ast, os

root = "backend"
base_pkgs = {"backend"}
stdlib = {"__future__", "typing", "collections", "dataclasses", "datetime", "hashlib",
           "json", "logging", "os", "pathlib", "re", "time", "abc", "enum", "functools",
           "io", "math", "random", "statistics", "string", "sys", "textwrap", "threading",
           "traceback", "uuid", "warnings", "zoneinfo", "copy", "itertools", "decimal",
           "fractions", "pprint", "bisect", "array", "struct", "pickle", "shelve",
           "heapq", "operator", "inspect", "weakref", "types", "gc", "configparser",
           "argparse", "http", "urllib", "base64", "binascii", "html", "csv", "zipfile",
           "tarfile", "shutil", "glob", "fnmatch", "tempfile", "shlex", "subprocess",
           "venv", "stat", "filecmp", "difflib", "codecs", "unicodedata", "keyword",
           "token", "tokenize", "dis", "pickletools"}

issues = []
for dirpath, _, filenames in os.walk(root):
    for f in filenames:
        if not f.endswith(".py"):
            continue
        filepath = os.path.join(dirpath, f)
        try:
            tree = ast.parse(open(filepath, encoding="utf-8").read())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.level == 0:
                module = node.module
                if module and module.split(".")[0] not in base_pkgs and module.split(".")[0] not in stdlib:
                    issues.append((filepath, node.lineno, ast.unparse(node)))

issues.sort(key=lambda x: (x[0], x[1]))
for i, l, t in issues:
    print(f"{i}:{l}: {t}")
