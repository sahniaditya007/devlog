from datetime import datetime, timezone
from enum import Enum as PyEnum
from app import db


class DecisionStatus(str, PyEnum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    DEPRECATED = "deprecated"
    SUPERSEDED = "superseded"


# Define valid state machine transitions
VALID_TRANSITIONS = {
    DecisionStatus.PROPOSED: {DecisionStatus.ACCEPTED, DecisionStatus.DEPRECATED},
    DecisionStatus.ACCEPTED: {DecisionStatus.DEPRECATED, DecisionStatus.SUPERSEDED},
    DecisionStatus.DEPRECATED: set(),
    DecisionStatus.SUPERSEDED: set(),
}


class Decision(db.Model):
    __tablename__ = "decisions"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    context = db.Column(db.Text, nullable=False)
    decision_text = db.Column(db.Text, nullable=False)
    consequences = db.Column(db.Text, nullable=True)
    tags = db.Column(db.JSON, nullable=False, default=list)
    ai_summary = db.Column(db.Text, nullable=True)
    status = db.Column(
        db.Enum(DecisionStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=DecisionStatus.PROPOSED,
    )

    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    project = db.relationship("Project", back_populates="decisions")
    author = db.relationship("User", back_populates="decisions")
    outgoing_links = db.relationship(
        "DecisionLink",
        foreign_keys="DecisionLink.source_id",
        back_populates="source",
        cascade="all, delete-orphan",
    )
    incoming_links = db.relationship(
        "DecisionLink",
        foreign_keys="DecisionLink.target_id",
        back_populates="target",
        cascade="all, delete-orphan",
    )

    def transition_to(self, new_status: DecisionStatus) -> None:
        """Enforce the state machine. Raises ValueError on invalid transition."""
        allowed = VALID_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise ValueError(
                f"Cannot transition from '{self.status.value}' to '{new_status.value}'. "
                f"Allowed: {[s.value for s in allowed] or 'none (terminal state)'}."
            )
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return f"<Decision id={self.id} status={self.status.value!r} title={self.title!r}>"
