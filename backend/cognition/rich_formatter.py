"""
VELYNX Phase 33 — Rich Terminal Formatter
Beautiful, information-dense terminal output with ASCII art and ANSI colors.
"""

from __future__ import annotations

import os
import re
import sys
import textwrap
from dataclasses import dataclass
from typing import Optional

# Force UTF-8 output on Windows to support box-drawing characters
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        os.environ.setdefault("PYTHONIOENCODING", "utf-8")


# ── ANSI Colors ──────────────────────────────────────────────────────────────
class _C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    CYAN    = "\033[96m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    WHITE   = "\033[97m"
    GRAY    = "\033[90m"


WIDTH = 70  # Max answer width


@dataclass
class FormattedOutput:
    output: str
    type_detected: str


class RichFormatter:
    """Formats answers for beautiful terminal display."""

    def format(self, query: str, answer: str, result: dict) -> FormattedOutput:
        """Detect content type and apply formatting."""
        from cognition.answer_classifier import AnswerClassifier
        classifier = AnswerClassifier()
        answer_type = classifier.classify(query, answer)

        try:
            if answer_type == "math_equation":
                output = self._format_math(answer, query)
            elif answer_type == "code_snippet":
                output = self._format_code(answer)
            elif answer_type == "comparison":
                output = self._format_comparison(answer, query)
            elif answer_type == "list":
                output = self._format_list(answer)
            elif answer_type == "concept":
                output = self._format_concept(answer, result)
            elif answer_type == "timeline":
                output = self._format_timeline(answer)
            elif answer_type == "how_to":
                output = self._format_steps(answer)
            else:
                output = self._format_general(answer)
        except Exception:
            output = self._format_general(answer)

        return FormattedOutput(output=output, type_detected=answer_type)

    def _format_math(self, answer: str, query: str) -> str:
        """Format math equations in ASCII art boxes."""
        lines = []
        lines.append(f"  {_C.CYAN}{_C.BOLD}┌{'─' * (WIDTH - 4)}┐{_C.RESET}")

        # Title
        title = "Mathematical Answer"
        lines.append(f"  {_C.CYAN}│{_C.RESET} {_C.BOLD}{title}{_C.RESET}{' ' * (WIDTH - len(title) - 5)}{_C.CYAN}│{_C.RESET}")
        lines.append(f"  {_C.CYAN}├{'─' * (WIDTH - 4)}┤{_C.RESET}")

        # Format equations with colors
        for line in answer.split("\n"):
            wrapped = textwrap.wrap(line.strip(), width=WIDTH - 6)
            for w in wrapped or [""]:
                colored = self._color_math(w)
                padding = WIDTH - len(w) - 6
                lines.append(f"  {_C.CYAN}│{_C.RESET} {colored}{' ' * max(0, padding)}{_C.CYAN}│{_C.RESET}")

        lines.append(f"  {_C.CYAN}└{'─' * (WIDTH - 4)}┘{_C.RESET}")
        return "\n".join(lines)

    def _color_math(self, text: str) -> str:
        """Color math expressions: variables=cyan, operators=yellow, numbers=green."""
        result = []
        i = 0
        while i < len(text):
            ch = text[i]
            if ch.isdigit():
                j = i
                while j < len(text) and (text[j].isdigit() or text[j] == "."):
                    j += 1
                result.append(f"{_C.GREEN}{text[i:j]}{_C.RESET}")
                i = j
            elif ch in "+-*/=^×÷±∑∏∫≈≠≤≥":
                result.append(f"{_C.YELLOW}{ch}{_C.RESET}")
                i += 1
            elif ch.isalpha() and ch.isupper():
                result.append(f"{_C.CYAN}{ch}{_C.RESET}")
                i += 1
            else:
                result.append(ch)
                i += 1
        return "".join(result)

    def _format_code(self, answer: str) -> str:
        """Format code with syntax highlighting."""
        # Extract code blocks
        code_match = re.search(r"```(?:\w+)?\n(.*?)```", answer, re.DOTALL)
        if code_match:
            code = code_match.group(1).strip()
        else:
            code = answer

        lines = []
        lines.append(f"  {_C.GRAY}┌─ Code ─{'─' * (WIDTH - 11)}┐{_C.RESET}")

        for i, line in enumerate(code.split("\n"), 1):
            highlighted = self._highlight_code(line)
            num = f"{_C.GRAY}{i:3}│{_C.RESET}"
            lines.append(f"  {num} {highlighted}")

        lines.append(f"  {_C.GRAY}└{'─' * (WIDTH - 4)}┘{_C.RESET}")
        return "\n".join(lines)

    def _highlight_code(self, line: str) -> str:
        """Syntax highlight a single line of code."""
        # Comments
        if line.strip().startswith("#") or line.strip().startswith("//"):
            return f"{_C.GRAY}{line}{_C.RESET}"

        result = line
        # Keywords
        keywords = ["def", "class", "if", "elif", "else", "for", "while", "return",
                     "import", "from", "try", "except", "with", "as", "yield", "lambda",
                     "function", "const", "let", "var", "async", "await"]
        for kw in keywords:
            result = re.sub(rf"\b{kw}\b", f"{_C.YELLOW}{kw}{_C.RESET}", result)

        # Strings
        result = re.sub(r'"([^"]*)"', f'{_C.GREEN}"\\1"{_C.RESET}', result)
        result = re.sub(r"'([^']*)'", f"{_C.GREEN}'\\1'{_C.RESET}", result)

        # Numbers
        result = re.sub(r"\b(\d+\.?\d*)\b", f"{_C.CYAN}\\1{_C.RESET}", result)

        return result

    def _format_comparison(self, answer: str, query: str) -> str:
        """Format comparison as a structured table."""
        # Extract comparison items
        comp = re.search(r"compare\s+(\w+)\s+(?:vs?\.?|versus|and)\s+(\w+)", query, re.IGNORECASE)
        if not comp:
            comp = re.search(r"(\w+)\s+(?:vs?\.?|versus)\s+(\w+)", query, re.IGNORECASE)
        if not comp:
            return self._format_general(answer)

        item_a = comp.group(1).strip().title()
        item_b = comp.group(2).strip().title()

        # Look up KG for domain info
        node_a = node_b = None
        try:
            from memory.knowledge_graph import knowledge_graph
            node_a = knowledge_graph.lookup(item_a)
            node_b = knowledge_graph.lookup(item_b)
        except Exception:
            pass

        # Build structured rows
        rows = []
        rows.append(("Type", item_a, item_b))
        rows.append(("Domain",
                      node_a.domain.replace("_", " ").title() if node_a else "General",
                      node_b.domain.replace("_", " ").title() if node_b else "General"))

        # Extract short facts from answer
        a_lower = item_a.lower()
        b_lower = item_b.lower()
        for sent in re.split(r"[.!]\s+", answer):
            sent = sent.strip()
            if not sent or len(sent) > 60:
                continue
            s_lower = sent.lower()
            if a_lower in s_lower and b_lower not in s_lower:
                rows.append((f"About {item_a}", sent[:20], ""))
            elif b_lower in s_lower and a_lower not in s_lower:
                rows.append((f"About {item_b}", "", sent[:20]))
            elif "dynamic" in s_lower or "type" in s_lower:
                rows.append(("Typing", sent[:20] if a_lower in s_lower else "", sent[:20] if b_lower in s_lower else sent[:20]))
            elif "use" in s_lower or "primary" in s_lower or "popular" in s_lower:
                rows.append(("Primary Use", sent[:20], sent[:20]))

        # Render table
        col_w = 20
        lines = []
        lines.append(f"  {_C.CYAN}┌{'─' * col_w}┬{'─' * col_w}┬{'─' * col_w}┐{_C.RESET}")
        lines.append(f"  {_C.CYAN}│{_C.RESET}{_C.BOLD}{'Feature':^{col_w}}{_C.RESET}{_C.CYAN}│{_C.RESET}{_C.BOLD}{item_a:^{col_w}}{_C.RESET}{_C.CYAN}│{_C.RESET}{_C.BOLD}{item_b:^{col_w}}{_C.RESET}{_C.CYAN}│{_C.RESET}")
        lines.append(f"  {_C.CYAN}├{'─' * col_w}┼{'─' * col_w}┼{'─' * col_w}┤{_C.RESET}")
        for label, va, vb in rows[:6]:
            lines.append(f"  {_C.CYAN}│{_C.RESET}{label:<{col_w}}{_C.CYAN}│{_C.RESET}{va:<{col_w}}{_C.CYAN}│{_C.RESET}{vb:<{col_w}}{_C.CYAN}│{_C.RESET}")
        lines.append(f"  {_C.CYAN}└{'─' * col_w}┴{'─' * col_w}┴{'─' * col_w}┘{_C.RESET}")
        return "\n".join(lines)

    def _format_list(self, answer: str) -> str:
        """Format list items with colored bullets."""
        lines = []
        for line in answer.split("\n"):
            stripped = line.strip()
            if re.match(r"^[-•◆▪]\s+", stripped):
                item = re.sub(r"^[-•◆▪]\s+", "", stripped)
                lines.append(f"  {_C.CYAN}◆{_C.RESET} {item}")
            elif re.match(r"^\d+[\.\)]\s+", stripped):
                lines.append(f"  {_C.GREEN}{stripped[:3]}{_C.RESET} {stripped[3:]}")
            elif stripped:
                lines.append(f"    {stripped}")
        return "\n".join(lines)

    def _format_concept(self, answer: str, result: dict) -> str:
        """Format as concept box with WHAT/HOW/WHY sections."""
        # Extract concept info from result
        concept = result.get("concept", {})
        depth = concept.get("depth", "") if concept else ""
        domain = concept.get("domain", "") if concept else ""
        connects = concept.get("connects_to", []) if concept else []
        conf = result.get("confidence", "")

        lines = []
        lines.append(f"  {_C.CYAN}{_C.BOLD}╔{'═' * (WIDTH - 4)}╗{_C.RESET}")

        # Title
        title = answer[:50].split(".")[0].strip()
        if len(title) > WIDTH - 8:
            title = title[:WIDTH - 11] + "..."
        lines.append(f"  {_C.CYAN}║{_C.RESET} {_C.BOLD}{_C.WHITE}{title}{_C.RESET}{' ' * max(0, WIDTH - len(title) - 6)}{_C.CYAN}║{_C.RESET}")

        # Metadata
        if domain or conf:
            meta = f"{_C.GRAY}Domain: {domain}  Conf: {conf}{_C.RESET}"
            meta_plain = f"Domain: {domain}  Conf: {conf}"
            lines.append(f"  {_C.CYAN}║{_C.RESET} {meta}{' ' * max(0, WIDTH - len(meta_plain) - 6)}{_C.CYAN}║{_C.RESET}")
        if depth:
            depth_str = f"{_C.GREEN}Depth: {depth}{_C.RESET}"
            depth_plain = f"Depth: {depth}"
            lines.append(f"  {_C.CYAN}║{_C.RESET} {depth_str}{' ' * max(0, WIDTH - len(depth_plain) - 6)}{_C.CYAN}║{_C.RESET}")

        lines.append(f"  {_C.CYAN}╠{'═' * (WIDTH - 4)}╣{_C.RESET}")

        # Answer body
        for line in answer.split("\n"):
            wrapped = textwrap.wrap(line.strip(), width=WIDTH - 6)
            for w in wrapped or [""]:
                padding = WIDTH - len(w) - 6
                lines.append(f"  {_C.CYAN}║{_C.RESET} {w}{' ' * max(0, padding)}{_C.CYAN}║{_C.RESET}")

        # Connections
        if connects:
            lines.append(f"  {_C.CYAN}╠{'═' * (WIDTH - 4)}╣{_C.RESET}")
            conn_str = " → ".join(connects[:4])
            conn_text = f"Connected to: {conn_str}"
            lines.append(f"  {_C.CYAN}║{_C.RESET} {_C.GRAY}{conn_text}{_C.RESET}{' ' * max(0, WIDTH - len(conn_text) - 6)}{_C.CYAN}║{_C.RESET}")

        lines.append(f"  {_C.CYAN}╚{'═' * (WIDTH - 4)}╝{_C.RESET}")
        return "\n".join(lines)

    def _format_timeline(self, answer: str) -> str:
        """Format dates as ASCII timeline."""
        lines = []
        lines.append(f"  {_C.CYAN}{_C.BOLD}Timeline{_C.RESET}")
        lines.append(f"  {_C.GRAY}{'─' * (WIDTH - 4)}{_C.RESET}")

        for sent in re.split(r"[.!]\s+", answer):
            dates = re.findall(r"\b((?:1[5-9]|20)\d{2})\b", sent)
            if dates:
                year = dates[0]
                event = re.sub(r"\b(?:1[5-9]|20)\d{2}\b", "", sent).strip(" ,.-")
                event = re.sub(r"^(In|in|During|during)\s+", "", event)
                event = event[:WIDTH - 15]
                lines.append(f"  {_C.GREEN}{year}{_C.RESET} {_C.CYAN}──●{_C.RESET} {event}")

        return "\n".join(lines)

    def _format_steps(self, answer: str) -> str:
        """Format step-by-step instructions."""
        # Split on "Step N:" if all on one line
        if "\n" not in answer and re.search(r"Step \d+", answer, re.IGNORECASE):
            answer = re.sub(r"(?=Step \d+)", "\n", answer, flags=re.IGNORECASE).strip()
        # Also split on ". Step N:"
        answer = re.sub(r"\.\s+(?=Step \d+)", "\n", answer, flags=re.IGNORECASE)

        lines = []
        step_num = 0

        for line in answer.split("\n"):
            stripped = line.strip()
            if not stripped:
                continue

            # Detect step headers
            step_match = re.match(r"^(?:step\s*)?(\d+)[\.\):]\s*(.+)", stripped, re.IGNORECASE)
            if step_match:
                step_num += 1
                lines.append(f"")
                lines.append(f"  {_C.GREEN}{_C.BOLD}Step {step_match.group(1)}:{_C.RESET} {step_match.group(2)}")
            elif re.match(r"^[-•]\s+", stripped):
                item = re.sub(r"^[-•]\s+", "", stripped)
                lines.append(f"        {_C.GRAY}└─{_C.RESET} {item}")
            elif step_num > 0:
                lines.append(f"        {stripped}")
            else:
                lines.append(f"  {stripped}")

        return "\n".join(lines)

    def _format_general(self, answer: str) -> str:
        """Format general prose with word wrapping."""
        lines = []
        for para in answer.split("\n\n"):
            wrapped = textwrap.fill(para.strip(), width=WIDTH - 4)
            for line in wrapped.split("\n"):
                lines.append(f"  {line}")
            lines.append("")
        return "\n".join(lines).rstrip()
