"""Business logic for decisions, kept separate from route handlers."""
from __future__ import annotations

from typing import Optional

from app import db
from app.models.decision import Decision, DecisionStatus
from app.models.decision_link import DecisionLink
from app.services import ai_service


def create_decision(
    title: str,
    context: str,
    decision_text: str,
    consequences: Optional[str],
    tags: list[str],
    project_id: int,
    author_id: int,
    enrich_with_ai: bool = True,
) -> Decision:
    """Create and persist a new decision, optionally enriching with AI."""
    decision = Decision(
        title=title,
        context=context,
        decision_text=decision_text,
        consequences=consequences,
        tags=tags,
        project_id=project_id,
        author_id=author_id,
        status=DecisionStatus.PROPOSED,
    )

    if enrich_with_ai:
        summary = ai_service.generate_summary(title, context, decision_text, consequences or "")
        if summary:
            decision.ai_summary = summary
        if not tags:
            suggested = ai_service.suggest_tags(title, context, decision_text)
            if suggested:
                decision.tags = suggested

    db.session.add(decision)
    db.session.commit()
    return decision


def transition_status(decision: Decision, new_status_value: str) -> Decision:
    """Apply a status transition, enforcing the state machine."""
    new_status = DecisionStatus(new_status_value)
    decision.transition_to(new_status)
    db.session.commit()
    return decision


def add_link(source: Decision, target_id: int, link_type: str) -> DecisionLink:
    """Create a directed link between two decisions."""
    if source.id == target_id:
        raise ValueError("A decision cannot link to itself.")
    if link_type not in DecisionLink.VALID_LINK_TYPES:
        raise ValueError(f"Invalid link_type '{link_type}'.")

    existing = DecisionLink.query.filter_by(
        source_id=source.id, target_id=target_id, link_type=link_type
    ).first()
    if existing:
        raise ValueError("This link already exists.")

    link = DecisionLink(source_id=source.id, target_id=target_id, link_type=link_type)
    db.session.add(link)
    db.session.commit()
    return link


def serialize_decision(decision: Decision) -> dict:
    """Return a dict representation of a decision including related data."""
    outgoing = [
        {
            "id": lnk.id,
            "direction": "outgoing",
            "link_type": lnk.link_type,
            "related_id": lnk.target_id,
            "related_title": lnk.target.title if lnk.target else None,
        }
        for lnk in decision.outgoing_links
    ]
    incoming = [
        {
            "id": lnk.id,
            "direction": "incoming",
            "link_type": lnk.link_type,
            "related_id": lnk.source_id,
            "related_title": lnk.source.title if lnk.source else None,
        }
        for lnk in decision.incoming_links
    ]
    return {
        "id": decision.id,
        "title": decision.title,
        "context": decision.context,
        "decision_text": decision.decision_text,
        "consequences": decision.consequences,
        "tags": decision.tags or [],
        "ai_summary": decision.ai_summary,
        "status": decision.status.value,
        "project_id": decision.project_id,
        "author_id": decision.author_id,
        "author_name": decision.author.name if decision.author else None,
        "created_at": decision.created_at.isoformat(),
        "updated_at": decision.updated_at.isoformat(),
        "links": outgoing + incoming,
    }
