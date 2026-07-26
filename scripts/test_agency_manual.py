from backend.agency.code_writer import CodeWriter
import os

writer = CodeWriter()
code = "def add(x, y): return x + y\nprint(add(2, 2))"
writer.propose_code_write(
    filepath=os.path.join(writer.ALLOWED_DIR, "test_calc.py"),
    code_content=code,
    reason="Manual unit test of agency sandbox.",
)
