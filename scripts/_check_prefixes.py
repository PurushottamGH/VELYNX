import os

count = 0
for dirpath, _, files in os.walk("backend"):
    for f in files:
        if not f.endswith(".py"):
            continue
        p = os.path.join(dirpath, f)
        with open(p, encoding="utf-8") as fh:
            c = fh.read()
        if "backend.backend." in c:
            print(f"DOUBLE PREFIX: {p}")
            count += 1
if count == 0:
    print("No double prefixes found. All clean.")
else:
    print(f"\n{count} files have double prefixes!")
