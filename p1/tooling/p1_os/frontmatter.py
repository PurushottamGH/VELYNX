"""Strict YAML-frontmatter Markdown loading, heading validation, and
deterministic serialization (spec sections 16, 17, 18).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel

from .schemas import UnknownObjectTypeError, schema_for_object_type

UTF8_BOM = b"\xef\xbb\xbf"

_MERGE_CONFLICT_MARKERS = ("<<<<<<<", "=======", ">>>>>>>")


class FrontmatterError(ValueError):
    """Base class for canonical-document parse failures."""


class EncodingError(FrontmatterError):
    pass


class MergeConflictMarkerError(FrontmatterError):
    pass


class DelimiterError(FrontmatterError):
    pass


class LineEndingError(FrontmatterError):
    pass


class YamlSafetyError(FrontmatterError):
    pass


class HeadingError(FrontmatterError):
    pass


# ---------------------------------------------------------------------------
# CanonicalDocument
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CanonicalDocument:
    record: BaseModel
    body: str
    line_ending: str  # "LF" or "CRLF"
    final_newline: bool
    source_path: Path | None = None


# ---------------------------------------------------------------------------
# Strict YAML loader: duplicate-key detection at every depth, no aliases,
# no merge keys, unsafe tags rejected via SafeLoader's restricted registry.
# ---------------------------------------------------------------------------


class _StrictSafeLoader(yaml.SafeLoader):
    pass


def _construct_mapping_no_duplicates(loader: yaml.SafeLoader, node: yaml.Node, deep: bool = False) -> dict:
    if not isinstance(node, yaml.MappingNode):
        raise yaml.constructor.ConstructorError(
            None, None, f"expected a mapping node, but found {node.id}", node.start_mark
        )
    loader.flatten_mapping(node)
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=True)
        try:
            hash(key)
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found unhashable key: {exc}",
                key_node.start_mark,
            ) from exc
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key: {key!r}",
                key_node.start_mark,
            )
        value = loader.construct_object(value_node, deep=deep)
        mapping[key] = value
    return mapping


def _flatten_mapping_reject_merge_keys(loader: yaml.SafeLoader, node: yaml.MappingNode) -> None:
    for key_node, _value_node in node.value:
        if key_node.tag == "tag:yaml.org,2002:merge":
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "merge keys ('<<') are not allowed",
                key_node.start_mark,
            )
    return yaml.SafeLoader.flatten_mapping(loader, node)


def _compose_node_reject_aliases(loader: yaml.SafeLoader, parent: yaml.Node | None, index: Any) -> yaml.Node:
    # PyYAML's composed Node objects do not carry an `.anchor` attribute;
    # anchor/alias information only exists on the (peeked) event, so it
    # must be inspected here, before delegating to the real composer.
    event = loader.peek_event()
    if isinstance(event, yaml.events.AliasEvent):
        raise yaml.composer.ComposerError(
            None, None, "aliases are not allowed", event.start_mark
        )
    anchor = getattr(event, "anchor", None)
    if anchor:
        raise yaml.composer.ComposerError(
            None, None, f"anchors are not allowed: &{anchor}", event.start_mark
        )
    return yaml.SafeLoader.compose_node(loader, parent, index)


_StrictSafeLoader.construct_mapping = _construct_mapping_no_duplicates
_StrictSafeLoader.flatten_mapping = _flatten_mapping_reject_merge_keys
_StrictSafeLoader.compose_node = _compose_node_reject_aliases


def load_yaml_mapping(yaml_text: str) -> dict[str, Any]:
    """Strictly parse a YAML frontmatter block into a mapping.

    Rejects empty YAML, non-mapping YAML, duplicate keys at any nesting
    depth, unsafe tags, aliases, and merge keys. Never silently repairs.
    """
    try:
        data = yaml.load(yaml_text, Loader=_StrictSafeLoader)
    except yaml.YAMLError as exc:
        raise YamlSafetyError(f"Malformed YAML frontmatter: {exc}") from exc

    if data is None:
        raise YamlSafetyError("YAML frontmatter must not be empty")
    if not isinstance(data, dict):
        raise YamlSafetyError(f"YAML frontmatter must be a mapping, found {type(data).__name__}")
    return data


# ---------------------------------------------------------------------------
# Encoding, merge-conflict markers, line endings, delimiters
# ---------------------------------------------------------------------------


def _decode_strict_utf8(raw: bytes) -> str:
    if raw.startswith(UTF8_BOM):
        raise EncodingError("UTF-8 BOM is not allowed")
    try:
        return raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise EncodingError(f"File is not valid UTF-8: {exc}") from exc


def _check_no_merge_conflict_markers(text: str) -> None:
    for line in text.splitlines():
        if line.startswith(_MERGE_CONFLICT_MARKERS):
            raise MergeConflictMarkerError(f"Unresolved merge-conflict marker found: {line!r}")


def _detect_line_ending(text: str) -> str:
    crlf_count = text.count("\r\n")
    lf_count = text.count("\n") - crlf_count
    cr_count = text.count("\r") - crlf_count

    if crlf_count > 0 and (lf_count > 0 or cr_count > 0):
        raise LineEndingError("Mixed line endings are not allowed")
    if cr_count > 0:
        raise LineEndingError("Lone CR line endings are not allowed")
    if crlf_count > 0:
        return "CRLF"
    return "LF"


def _split_frontmatter(text: str, newline: str) -> tuple[str, str]:
    """Split into (yaml_text, body). Both delimiter lines must be exactly '---'."""
    opening = f"---{newline}"
    if not text.startswith(opening):
        raise DelimiterError("Canonical files must begin with '---' at byte one")

    rest = text[len(opening):]

    search_start = 0
    closing_span: tuple[int, int] | None = None
    while search_start <= len(rest):
        pos = rest.find(newline, search_start)
        if pos == -1:
            line = rest[search_start:]
            line_end = len(rest)
        else:
            line = rest[search_start:pos]
            line_end = pos + len(newline)

        if line == "---":
            closing_span = (search_start, line_end)
            break
        if pos == -1:
            break
        search_start = line_end

    if closing_span is None:
        raise DelimiterError("Unterminated YAML frontmatter: no closing '---' found")

    yaml_text = rest[: closing_span[0]]
    body = rest[closing_span[1]:]
    return yaml_text, body


# ---------------------------------------------------------------------------
# Heading validation
# ---------------------------------------------------------------------------


def _extract_level2_headings(body: str, newline: str) -> list[str]:
    headings: list[str] = []
    in_fence = False
    fence_char = ""
    fence_len = 0

    for line in body.split(newline):
        stripped_leading = line.lstrip(" \t")
        leading_len = len(line) - len(stripped_leading)

        if not in_fence:
            fence_match_char = None
            if stripped_leading.startswith("```"):
                fence_match_char = "`"
            elif stripped_leading.startswith("~~~"):
                fence_match_char = "~"
            if fence_match_char is not None:
                run_len = len(stripped_leading) - len(stripped_leading.lstrip(fence_match_char))
                if run_len >= 3:
                    in_fence = True
                    fence_char = fence_match_char
                    fence_len = run_len
                    continue

            if leading_len == 0 and line.startswith("## "):
                headings.append(line.rstrip(" \t"))
        else:
            candidate = stripped_leading.rstrip(" \t")
            if candidate and set(candidate) == {fence_char} and len(candidate) >= fence_len:
                in_fence = False
                fence_char = ""
                fence_len = 0

    if in_fence:
        raise HeadingError("Unterminated fenced code block in document body")

    return headings


def validate_headings(body: str, required_headings: tuple[str, ...], newline: str = "\n") -> None:
    """Validate that `body` contains exactly `required_headings`, in order,
    outside of fenced code blocks (spec section 18)."""
    discovered = _extract_level2_headings(body, newline)
    required_set = set(required_headings)
    discovered_required_subsequence = [h for h in discovered if h in required_set]

    if discovered_required_subsequence != list(required_headings):
        raise HeadingError(
            "Required headings missing, duplicated, or out of order. "
            f"Expected {list(required_headings)!r}, found relevant headings "
            f"{discovered_required_subsequence!r}"
        )


# ---------------------------------------------------------------------------
# Parsing entry point
# ---------------------------------------------------------------------------


def parse_document(raw: bytes, *, source_path: Path | None = None) -> CanonicalDocument:
    text = _decode_strict_utf8(raw)
    _check_no_merge_conflict_markers(text)

    line_ending = _detect_line_ending(text)
    newline = "\r\n" if line_ending == "CRLF" else "\n"

    yaml_text, body = _split_frontmatter(text, newline)
    mapping = load_yaml_mapping(yaml_text)

    object_type = mapping.get("object_type")
    if not isinstance(object_type, str):
        raise YamlSafetyError("YAML frontmatter must contain a string 'object_type' field")

    try:
        schema_cls = schema_for_object_type(object_type)
    except UnknownObjectTypeError as exc:
        raise YamlSafetyError(str(exc)) from exc

    record = schema_cls.model_validate(mapping)
    validate_headings(body, schema_cls.REQUIRED_HEADINGS, newline=newline)

    final_newline = text.endswith(newline)

    return CanonicalDocument(
        record=record,
        body=body,
        line_ending=line_ending,
        final_newline=final_newline,
        source_path=source_path,
    )


# ---------------------------------------------------------------------------
# Deterministic serialization
# ---------------------------------------------------------------------------


class _Quoted(str):
    """Marker subclass forcing double-quoted scalar style on dump."""


class _StrictSafeDumper(yaml.SafeDumper):
    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        # Canonical style indents block-sequence items under their parent
        # mapping key (matches every hand-authored fixture and template);
        # PyYAML's default is flush-left ("indentless") sequences.
        return super().increase_indent(flow=flow, indentless=False)


def _represent_quoted(dumper: yaml.SafeDumper, data: _Quoted) -> yaml.ScalarNode:
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data), style='"')


def _represent_none(dumper: yaml.SafeDumper, data: None) -> yaml.ScalarNode:
    return dumper.represent_scalar("tag:yaml.org,2002:null", "null")


_StrictSafeDumper.add_representer(_Quoted, _represent_quoted)
_StrictSafeDumper.add_representer(type(None), _represent_none)


def _format_datetime(value: datetime) -> str:
    """ISO-8601 text for `value` (spec sections 17, Milestone 1.1 task 2).

    UTC instants render with a trailing 'Z'; non-UTC offsets render as an
    explicit '+HH:MM'/'-HH:MM'. `datetime.isoformat()` already preserves
    fractional seconds and produces an explicit offset for non-UTC zones,
    so only the UTC case needs rewriting.
    """
    text = value.isoformat()
    if value.utcoffset() == timedelta(0) and text.endswith("+00:00"):
        text = text[: -len("+00:00")] + "Z"
    return text


def _to_plain(value: Any) -> Any:
    if isinstance(value, BaseModel):
        result: dict[str, Any] = {}
        for field_name in value.__class__.model_fields:
            result[field_name] = _to_plain(getattr(value, field_name))
        return result
    if isinstance(value, datetime):
        return _Quoted(_format_datetime(value))
    if isinstance(value, date):
        return _Quoted(value.isoformat())
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, str):
        return str(value)
    if isinstance(value, bool):
        return value
    if isinstance(value, list):
        return [_to_plain(item) for item in value]
    if isinstance(value, dict):
        return {key: _to_plain(item) for key, item in value.items()}
    return value


def serialize_metadata(record: BaseModel) -> str:
    """Deterministic YAML frontmatter text for `record` (no delimiters).

    Common fields appear first in the fixed order, followed by
    object-specific fields in declaration order. Does not mutate `record`.
    """
    ordered: dict[str, Any] = {}
    field_names = list(record.__class__.model_fields.keys())
    for name in field_names:
        if name == "schema_version":
            ordered[name] = _Quoted(str(getattr(record, name)))
        else:
            ordered[name] = _to_plain(getattr(record, name))

    text = yaml.dump(
        ordered,
        Dumper=_StrictSafeDumper,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )
    return text.replace("\r\n", "\n")


def serialize_document(document: CanonicalDocument) -> str:
    """Deterministic full canonical text: LF delimiters + metadata + preserved body."""
    metadata_text = serialize_metadata(document.record)
    return f"---\n{metadata_text}---\n{document.body}"
