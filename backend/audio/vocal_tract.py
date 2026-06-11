"""
VELYNX Vocal Tract — offline Text-to-Speech
============================================

Deterministic, non-blocking TTS for the REPL.  Wraps the system ``pyttsx3``
engine (SAPI5 / NSSpeechSynthesizer / espeak) so VELYNX can read its own
deterministic outputs out loud without:

* burning GPU/VRAM (pyttsx3 uses native, OS-installed voices);
* hitting the network (no model downloads, no remote APIs);
* blocking the Rich terminal UI (synthesis runs on a worker thread).

The voice is intentionally tuned to a slightly slower, philosophical pace
so the words land like an oracle, not a stenographer.
"""

from __future__ import annotations

import logging
import re
import threading
from typing import Optional

import pyttsx3

logger = logging.getLogger("velynx.vocal_tract")

# Characters / glyphs that look pretty on screen but make the speech
# engine say "asterisk" / "open bracket" out loud.
_VISUAL_GLYPHS = re.compile(r"[*#\[\]|─_`>]+")

# Bulleted list lines start with "- " or "* " — drop them entirely.
_BULLET_PREFIX = re.compile(r"^\s*[-*•]\s+")

# Collapse runs of whitespace so the audio doesn't sound like a robot
# announcing "new line, new line".
_WHITESPACE_RUN = re.compile(r"\s+")

# Safety: never let a runaway string talk for ten minutes.
_MAX_CHARS = 4000


def _strip_visual_markdown(text: str) -> str:
    """Return ``text`` with table / markdown chrome removed for speaking.

    Examples
    --------
    >>> _strip_visual_markdown("| concept | score |")
    'concept score'
    >>> _strip_visual_markdown("**Identity** is a thread.")
    'Identity is a thread.'
    >>> _strip_visual_markdown("- *despair* relates to depression")
    'despair relates to depression'
    """

    if not text:
        return ""

    cleaned_lines: list[str] = []
    for raw_line in text.splitlines():
        line = _BULLET_PREFIX.sub("", raw_line)
        line = _VISUAL_GLYPHS.sub(" ", line)
        line = _WHITESPACE_RUN.sub(" ", line).strip()
        if line:
            cleaned_lines.append(line)

    return " ".join(cleaned_lines)


class VocalTract:
    """A thin, thread-friendly wrapper around :mod:`pyttsx3`.

    The underlying ``pyttsx3`` engine is **not** thread-safe to share
    directly — its ``say()`` / ``runAndWait()`` pair must happen on the
    same thread that initialised the engine.  We therefore:

    * Build the engine on the main thread inside ``__init__``;
    * Do the actual synthesis on a worker thread created by
      :meth:`speak_async` (which constructs its own engine per call,
      because re-using the parent's engine across threads triggers
      ``RuntimeError: run loop already started`` on most backends).
    """

    DEFAULT_RATE = 160
    DEFAULT_VOLUME = 0.9

    def __init__(
        self,
        rate: int = DEFAULT_RATE,
        volume: float = DEFAULT_VOLUME,
        voice_hint: Optional[str] = None,
        enabled: bool = True,
    ) -> None:
        self.rate = rate
        self.volume = volume
        self.voice_hint = voice_hint
        self.enabled = enabled

        # We construct *one* engine eagerly so misconfiguration (no TTS
        # driver installed, broken voice) is detected at startup, not on
        # the first speak call.  It is used only for warm-up; the
        # worker thread builds its own engine.
        self._engine: Optional[pyttsx3.Engine] = None
        self._worker_lock = threading.Lock()
        self._active_thread: Optional[threading.Thread] = None

        if self.enabled:
            try:
                self._engine = pyttsx3.init()
                self._configure_engine(self._engine)
            except Exception as exc:  # pragma: no cover - hardware-dependent
                logger.warning(
                    "[vocal_tract] Could not initialise pyttsx3 engine: %s. "
                    "Falling back to silent mode.",
                    exc,
                )
                self._engine = None
                self.enabled = False
        else:
            logger.info("[vocal_tract] Initialised in disabled mode (silent).")

    # ── Configuration helpers ─────────────────────────────────────────

    def _configure_engine(self, engine: "pyttsx3.Engine") -> None:
        engine.setProperty("rate", self.rate)
        engine.setProperty("volume", max(0.0, min(1.0, self.volume)))

        if self.voice_hint:
            try:
                voices = engine.getProperty("voices") or []
                target = self.voice_hint.lower()
                for voice in voices:
                    name = (getattr(voice, "name", "") or "").lower()
                    vid = (getattr(voice, "id", "") or "").lower()
                    if target in name or target in vid:
                        engine.setProperty("voice", voice.id)
                        return
                logger.info(
                    "[vocal_tract] Voice hint %r not found; using default.",
                    self.voice_hint,
                )
            except Exception as exc:  # pragma: no cover - backend-specific
                logger.debug("[vocal_tract] Voice selection failed: %s", exc)

    # ── Public API ────────────────────────────────────────────────────

    def speak(self, text: str) -> None:
        """Speak ``text`` synchronously on the current thread."""

        if not self.enabled:
            return

        clean = _strip_visual_markdown(text)
        if not clean:
            return

        if len(clean) > _MAX_CHARS:
            logger.info(
                "[vocal_tract] Truncating %d-char utterance to %d chars.",
                len(clean), _MAX_CHARS,
            )
            clean = clean[:_MAX_CHARS].rsplit(" ", 1)[0] + "."

        try:
            engine = pyttsx3.init()
            self._configure_engine(engine)
            engine.say(clean)
            engine.runAndWait()
            engine.stop()
        except Exception as exc:  # pragma: no cover - hardware-dependent
            logger.warning("[vocal_tract] speak() failed: %s", exc)

    def speak_async(self, text: str) -> threading.Thread:
        """Speak ``text`` on a background thread so the REPL stays live.

        Returns the worker thread so callers can ``.join()`` it for tests
        or graceful shutdown.  Only one async utterance runs at a time;
        if a previous one is still going, the new one is silently skipped
        (talking over VELYNX's own voice is rarely what we want).
        """

        if not self.enabled:
            # Hand back a finished dummy thread so callers can .join()
            # uniformly.
            thread = threading.Thread(
                target=lambda: None,
                name="vocal_tract.disabled",
                daemon=True,
            )
            thread.start()
            return thread

        clean = _strip_visual_markdown(text)
        if not clean:
            return self._spawn_dummy_thread()

        def _worker() -> None:
            try:
                engine = pyttsx3.init()
                self._configure_engine(engine)
                engine.say(clean)
                engine.runAndWait()
                engine.stop()
            except Exception as exc:  # pragma: no cover - hw-dependent
                logger.warning("[vocal_tract] async speak() failed: %s", exc)
            finally:
                with self._worker_lock:
                    self._active_thread = None

        with self._worker_lock:
            if self._active_thread is not None and self._active_thread.is_alive():
                logger.debug(
                    "[vocal_tract] Skipping new utterance; previous one still running."
                )
                return self._active_thread
            thread = threading.Thread(
                target=_worker,
                name="vocal_tract.speak",
                daemon=True,
            )
            self._active_thread = thread
            thread.start()
        return thread

    # ── Internal helpers ──────────────────────────────────────────────

    @staticmethod
    def _spawn_dummy_thread() -> threading.Thread:
        thread = threading.Thread(
            target=lambda: None,
            name="vocal_tract.noop",
            daemon=True,
        )
        thread.start()
        return thread

    def shutdown(self) -> None:
        """Stop the warm-up engine and wait for any pending utterance."""

        if self._active_thread is not None and self._active_thread.is_alive():
            self._active_thread.join(timeout=2.0)
        if self._engine is not None:
            try:
                self._engine.stop()
            except Exception:  # pragma: no cover - backend-specific
                pass


if __name__ == "__main__":
    # Smoke test: speak one synchronous, one async, both with stripped
    # markdown.  Output is hardware-dependent.
    tract = VocalTract()
    print("[vocal_tract] Rate:", tract.rate, "Volume:", tract.volume, "Enabled:", tract.enabled)
    tract.speak("| *Concept* | score |\n- **despair** relates to depression")
    thread = tract.speak_async("────────────────────────────────\n#  Identity is a thread.")
    print("[vocal_tract] Async thread:", thread.name, "alive:", thread.is_alive())
    thread.join(timeout=10.0)
    tract.shutdown()
