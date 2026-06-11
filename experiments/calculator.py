"""Simple CLI calculator."""
import sys


def main():
    if len(sys.argv) < 4:
        print("Usage: python calculator.py <num1> <op> <num2>")
        print("Operators: + - * /")
        sys.exit(1)
    a, op, b = float(sys.argv[1]), sys.argv[2], float(sys.argv[3])
    ops = {"+": a + b, "-": a - b, "*": a * b, "/": a / b if b != 0 else "Error: division by zero"}
    result = ops.get(op, f"Unknown operator: {op}")
    print(result)


if __name__ == "__main__":
    main()
