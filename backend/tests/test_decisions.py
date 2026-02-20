"""Tests for decision endpoints and state machine."""
import pytest
from app.models.decision import Decision, DecisionStatus, VALID_TRANSITIONS


class TestDecisionStateMachine:
    """Unit tests for the state machine — no HTTP involved."""

    def test_proposed_to_accepted(self, db, user, project):
        d = Decision(
            title="Use PostgreSQL",
            context="We need a relational DB",
            decision_text="Use PostgreSQL for all persistence.",
            project_id=project.id,
            author_id=user.id,
            status=DecisionStatus.PROPOSED,
            tags=[],
        )
        db.session.add(d)
        db.session.commit()
        d.transition_to(DecisionStatus.ACCEPTED)
        assert d.status == DecisionStatus.ACCEPTED

    def test_proposed_to_deprecated(self, db, user, project):
        d = Decision(
            title="Use MongoDB",
            context="Considered NoSQL",
            decision_text="Use MongoDB.",
            project_id=project.id,
            author_id=user.id,
            status=DecisionStatus.PROPOSED,
            tags=[],
        )
        db.session.add(d)
        db.session.commit()
        d.transition_to(DecisionStatus.DEPRECATED)
        assert d.status == DecisionStatus.DEPRECATED

    def test_invalid_transition_proposed_to_superseded(self, db, user, project):
        d = Decision(
            title="Bad transition",
            context="ctx",
            decision_text="dec",
            project_id=project.id,
            author_id=user.id,
            status=DecisionStatus.PROPOSED,
            tags=[],
        )
        db.session.add(d)
        db.session.commit()
        with pytest.raises(ValueError, match="Cannot transition"):
            d.transition_to(DecisionStatus.SUPERSEDED)

    def test_terminal_state_deprecated_cannot_transition(self, db, user, project):
        d = Decision(
            title="Terminal",
            context="ctx",
            decision_text="dec",
            project_id=project.id,
            author_id=user.id,
            status=DecisionStatus.DEPRECATED,
            tags=[],
        )
        db.session.add(d)
        db.session.commit()
        with pytest.raises(ValueError, match="terminal state"):
            d.transition_to(DecisionStatus.ACCEPTED)

    def test_all_valid_transitions_are_reachable(self):
        """Ensure the transition map covers all statuses."""
        for status in DecisionStatus:
            assert status in VALID_TRANSITIONS


class TestDecisionAPI:
    def _create_decision(self, client, auth_headers, project_id, **overrides):
        payload = {
            "title": "Use Redis for caching",
            "context": "Our API response times are slow under load.",
            "decision_text": "Introduce Redis as a caching layer.",
            "consequences": "Adds operational complexity.",
            "tags": ["performance", "infrastructure"],
            "project_id": project_id,
        }
        payload.update(overrides)
        return client.post("/api/decisions/", json=payload, headers=auth_headers)

    def _get_auth_headers(self, client, user):
        """Helper to get auth headers for a specific user."""
        resp = client.post("/api/auth/login", json={"email": user.email, "password": "password123"})
        token = resp.get_json()["token"]
        return {"Authorization": f"Bearer {token}"}

    def test_create_decision_success(self, client, auth_headers, project):
        resp = self._create_decision(client, auth_headers, project.id)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["status"] == "proposed"
        assert data["title"] == "Use Redis for caching"
        assert "performance" in data["tags"]

    def test_create_decision_missing_required_fields(self, client, auth_headers, project):
        resp = client.post("/api/decisions/", json={"project_id": project.id}, headers=auth_headers)
        assert resp.status_code == 422
        errors = resp.get_json()["errors"]
        assert "title" in errors
        assert "context" in errors
        assert "decision_text" in errors

    def test_create_decision_too_many_tags(self, client, auth_headers, project):
        resp = self._create_decision(
            client, auth_headers, project.id,
            tags=["t1", "t2", "t3", "t4", "t5", "t6", "t7", "t8", "t9", "t10", "t11"]
        )
        assert resp.status_code == 422

    def test_list_decisions_filtered_by_project(self, client, auth_headers, project):
        self._create_decision(client, auth_headers, project.id)
        self._create_decision(client, auth_headers, project.id, title="Another decision")
        resp = client.get(f"/api/decisions/?project_id={project.id}", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.get_json()) == 2

    def test_get_decision(self, client, auth_headers, project):
        create_resp = self._create_decision(client, auth_headers, project.id)
        decision_id = create_resp.get_json()["id"]
        resp = client.get(f"/api/decisions/{decision_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["id"] == decision_id

    def test_status_transition_via_api(self, client, auth_headers, project):
        create_resp = self._create_decision(client, auth_headers, project.id)
        decision_id = create_resp.get_json()["id"]

        resp = client.patch(
            f"/api/decisions/{decision_id}/status",
            json={"status": "accepted"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "accepted"

    def test_invalid_status_transition_via_api(self, client, auth_headers, project):
        create_resp = self._create_decision(client, auth_headers, project.id)
        decision_id = create_resp.get_json()["id"]

        resp = client.patch(
            f"/api/decisions/{decision_id}/status",
            json={"status": "superseded"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_invalid_status_value_via_api(self, client, auth_headers, project):
        create_resp = self._create_decision(client, auth_headers, project.id)
        decision_id = create_resp.get_json()["id"]

        resp = client.patch(
            f"/api/decisions/{decision_id}/status",
            json={"status": "flying"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_update_decision_fields(self, client, auth_headers, project):
        create_resp = self._create_decision(client, auth_headers, project.id)
        decision_id = create_resp.get_json()["id"]

        resp = client.put(
            f"/api/decisions/{decision_id}",
            json={"title": "Updated Title", "tags": ["updated"]},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["title"] == "Updated Title"
        assert "updated" in data["tags"]

    def test_add_link_between_decisions(self, client, auth_headers, project):
        d1 = self._create_decision(client, auth_headers, project.id, title="Old Decision").get_json()
        d2 = self._create_decision(client, auth_headers, project.id, title="New Decision").get_json()

        resp = client.post(
            f"/api/decisions/{d2['id']}/links",
            json={"target_id": d1["id"], "link_type": "supersedes"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        links = resp.get_json()["links"]
        assert any(lnk["link_type"] == "supersedes" for lnk in links)

    def test_self_link_rejected(self, client, auth_headers, project):
        d = self._create_decision(client, auth_headers, project.id).get_json()
        resp = client.post(
            f"/api/decisions/{d['id']}/links",
            json={"target_id": d["id"], "link_type": "relates_to"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_invalid_link_type_rejected(self, client, auth_headers, project):
        d1 = self._create_decision(client, auth_headers, project.id).get_json()
        d2 = self._create_decision(client, auth_headers, project.id, title="D2").get_json()
        resp = client.post(
            f"/api/decisions/{d1['id']}/links",
            json={"target_id": d2["id"], "link_type": "invalidtype"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_cannot_link_to_other_users_decision(self, client, db, user, project):
        """Test that users cannot link to decisions from other users' projects."""
        from app.models.user import User
        from app.models.project import Project
        from app.models.decision import Decision, DecisionStatus
        
        # Create a second user and project
        other_user = User(email="other@example.com", name="Other User")
        other_user.set_password("password123")
        db.session.add(other_user)
        db.session.commit()
        
        other_project = Project(name="Other Project", owner_id=other_user.id)
        db.session.add(other_project)
        db.session.commit()
        
        # Create decisions: one for current user, one for other user
        auth_headers = self._get_auth_headers(client, user)
        d1 = self._create_decision(client, auth_headers, project.id).get_json()
        d2 = Decision(
            title="Other User Decision",
            context="Context",
            decision_text="Decision text",
            project_id=other_project.id,
            author_id=other_user.id,
            status=DecisionStatus.PROPOSED,
            tags=[],
        )
        db.session.add(d2)
        db.session.commit()
        
        # Try to link current user's decision to other user's decision
        resp = client.post(
            f"/api/decisions/{d1['id']}/links",
            json={"target_id": d2.id, "link_type": "relates_to"},
            headers=auth_headers,
        )
        assert resp.status_code == 403  # Access denied
        assert "Access denied" in resp.get_json()["error"]

    def test_search_decisions(self, client, auth_headers, project):
        self._create_decision(client, auth_headers, project.id, title="Redis caching strategy")
        self._create_decision(
            client, auth_headers, project.id,
            title="PostgreSQL selection",
            context="We need a relational database.",
            decision_text="Use PostgreSQL as the primary data store.",
        )
        resp = client.get("/api/decisions/?q=Redis", headers=auth_headers)
        assert resp.status_code == 200
        results = resp.get_json()
        assert len(results) == 1
        assert "redis" in results[0]["title"].lower()

    def test_delete_decision(self, client, auth_headers, project):
        create_resp = self._create_decision(client, auth_headers, project.id)
        decision_id = create_resp.get_json()["id"]
        resp = client.delete(f"/api/decisions/{decision_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert client.get(f"/api/decisions/{decision_id}", headers=auth_headers).status_code == 404

    def test_unauthenticated_access_denied(self, client, project):
        resp = client.get(f"/api/decisions/?project_id={project.id}")
        assert resp.status_code == 401
