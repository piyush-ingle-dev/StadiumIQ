"""GPT-4o integration service.

All calls to the OpenAI API are funneled through this module so that
caching, error handling, and background execution are applied
consistently everywhere the app needs an AI response (translation,
navigation guidance, operational insights).
"""

from __future__ import annotations

import hashlib
import logging
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any

from flask import current_app
from openai import OpenAI, OpenAIError

from app.extensions import cache

logger = logging.getLogger(__name__)

# A small worker pool lets us fire off AI calls (e.g. translation,
# recommendations) without blocking the request thread that kicked
# them off, which is what "async AI calls" means in a sync Flask app
# without pulling in a full async stack.
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="ai-worker")


class AIServiceError(RuntimeError):
    """Raised when the AI backend cannot fulfill a request."""


def _client() -> OpenAI:
    """Build an OpenAI client from the current app's configuration."""
    api_key = current_app.config.get("OPENAI_API_KEY")
    if not api_key:
        raise AIServiceError("OPENAI_API_KEY is not configured.")
    return OpenAI(api_key=api_key)


def _cache_key(prefix: str, payload: str) -> str:
    """Build a stable, short cache key for a given prompt payload."""
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]
    return f"ai:{prefix}:{digest}"


def _chat_completion(system_prompt: str, user_prompt: str, *, model: str) -> str:
    """Call the chat completion endpoint and return plain text content."""
    client = _client()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=500,
            temperature=0.3,
        )
    except OpenAIError as exc:
        logger.exception("OpenAI request failed")
        raise AIServiceError(str(exc)) from exc

    content = response.choices[0].message.content
    return (content or "").strip()


def get_translation(text: str, target_language: str) -> str:
    """Translate `text` into `target_language`, using the cache when possible.

    Args:
        text: The source text to translate.
        target_language: ISO-ish language code, e.g. "hi", "ar", "es", "fr".

    Returns:
        The translated string. Falls back to the original text if the
        AI backend is unavailable, so the UI never breaks.
    """
    key = _cache_key("translate", f"{target_language}:{text}")
    cached = cache.get(key)
    if cached is not None:
        return cached

    model = current_app.config.get("OPENAI_MODEL", "gpt-4o")
    system_prompt = (
        "You are a precise translation engine for a stadium fan-assistance app. "
        "Translate the user's message into the requested language. "
        "Return only the translated text with no extra commentary."
    )
    user_prompt = f"Target language code: {target_language}\nText: {text}"

    try:
        translated = _chat_completion(system_prompt, user_prompt, model=model)
    except AIServiceError:
        return text

    cache.set(key, translated, timeout=3600)
    return translated


def get_navigation_guidance(current_zone: str, destination: str, language: str = "en") -> str:
    """Ask the AI for concise walking directions between two stadium zones.

    Args:
        current_zone: Where the fan currently is (e.g. "Gate B").
        destination: Where they want to go (e.g. "Section 114").
        language: Language code for the response.

    Returns:
        A short, clear direction string.
    """
    key = _cache_key("nav", f"{language}:{current_zone}->{destination}")
    cached = cache.get(key)
    if cached is not None:
        return cached

    model = current_app.config.get("OPENAI_MODEL", "gpt-4o")
    system_prompt = (
        "You are a stadium navigation assistant for the FIFA World Cup 2026. "
        "Give short, clear, step-by-step walking directions (max 3 steps) "
        "between two points inside a large stadium. Respond in the requested "
        "language code."
    )
    user_prompt = (
        f"Language: {language}\nFrom: {current_zone}\nTo: {destination}\n"
        "Give practical directions a fan can follow."
    )

    try:
        guidance = _chat_completion(system_prompt, user_prompt, model=model)
    except AIServiceError:
        guidance = f"Head toward {destination} following the nearest overhead signage from {current_zone}."

    cache.set(key, guidance, timeout=1800)
    return guidance


def get_completion(system_prompt: str, user_prompt: str) -> str:
    """Run a one-off chat completion using the app's configured model.

    This is the public entry point for callers that need a custom
    system/user prompt pair (e.g. the operational insights briefing)
    rather than one of the specific helpers above. Raises
    AIServiceError on failure so callers can decide their own fallback.
    """
    model = current_app.config.get("OPENAI_MODEL", "gpt-4o")
    return _chat_completion(system_prompt, user_prompt, model=model)


def submit_background(fn, *args: Any, **kwargs: Any) -> Future:
    """Run a callable on the background worker pool inside the app context.

    Used for AI calls that don't need to block the HTTP response, such
    as pre-warming translation caches or generating operational
    insight summaries. The current Flask app is captured and pushed
    onto the worker thread so `current_app` remains usable inside `fn`.
    """
    app = current_app._get_current_object()  # type: ignore[attr-defined]

    def _run_with_context() -> Any:
        with app.app_context():
            return fn(*args, **kwargs)

    return _executor.submit(_run_with_context)
