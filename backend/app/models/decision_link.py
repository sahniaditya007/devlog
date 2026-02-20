from datetime import datetime, timezone
from app import db


class DecisionLink(db.Model):
    """Represents a directed relationship between two decisions (e.g. supersedes, relates-to)."""

    __tablename__ = "decision_links"

    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey("decisions.id"), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey("decisions.id"), nullable=False)
    link_type = db.Column(db.String(50), nullable=False)  # "supersedes" | "relates_to" | "blocked_by"
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("source_id", "target_id", "link_type", name="uq_decision_link"),
        db.CheckConstraint("source_id != target_id", name="ck_no_self_link"),
    )

    source = db.relationship("Decision", foreign_keys=[source_id], back_populates="outgoing_links")
    target = db.relationship("Decision", foreign_keys=[target_id], back_populates="incoming_links")

    VALID_LINK_TYPES = {"supersedes", "relates_to", "blocked_by"}

    def __repr__(self) -> str:
        return f"<DecisionLink {self.source_id} --{self.link_type}--> {self.target_id}>"
