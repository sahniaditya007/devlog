"""AI service for generating decision summaries and tag suggestions.

Gracefully degrades when OPENAI_API_KEY is not set — the rest of the
application remains fully functional without it.
"""
from __future__ import annotations

import logging
from typing import Optional

from flask import current_app

logger = logging.getLogger(__name__)


def _get_client():
    """Return an OpenAI client or None if the key is not configured."""
    api_key = current_app.config.get("OPENAI_API_KEY", "")
    if not api_key:
        return None
    try:
        from openai import OpenAI  # type: ignore
        return OpenAI(api_key=api_key)
    except Exception as exc:
        logger.warning("OpenAI client unavailable; AI features disabled: %s", exc)
        return None


def generate_summary(title: str, context: str, decision_text: str, consequences: str) -> Optional[str]:
    """Generate a concise AI summary for a decision record."""
    client = _get_client()
    if client is None:
        return None

    prompt = (
        "You are a technical writer helping engineering teams document decisions.\n"
        "Summarize the following Architecture Decision Record in 2-3 sentences.\n"
        "Be precise, neutral, and focus on the 'why'.\n\n"
        f"Title: {title}\n"
        f"Context: {context}\n"
        f"Decision: {decision_text}\n"
        f"Consequences: {consequences or 'Not specified'}\n"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        logger.error("AI summary generation failed: %s", exc)
        return None


def suggest_tags(title: str, context: str, decision_text: str) -> list[str]:
    """Suggest relevant tags for a decision record."""
    client = _get_client()
    if client is None:
        return []

    prompt = (
        "You are a technical assistant helping categorize engineering decisions.\n"
        "Given the following decision, suggest 3-5 short, lowercase tags (e.g. 'database', 'auth', 'performance').\n"
        "Return ONLY a comma-separated list of tags, nothing else.\n\n"
        f"Title: {title}\n"
        f"Context: {context}\n"
        f"Decision: {decision_text}\n"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60,
            temperature=0.2,
        )
        raw = response.choices[0].message.content.strip()
        return [tag.strip().lower() for tag in raw.split(",") if tag.strip()][:5]
    except Exception as exc:
        logger.error("AI tag suggestion failed: %s", exc)
        return []
