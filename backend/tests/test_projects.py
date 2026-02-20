"""Tests for project endpoints."""


class TestProjects:
    def test_create_project(self, client, auth_headers):
        resp = client.post("/api/projects/", json={"name": "My Project", "description": "Desc"}, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["name"] == "My Project"
        assert data["decision_count"] == 0

    def test_create_project_missing_name(self, client, auth_headers):
        resp = client.post("/api/projects/", json={"description": "No name"}, headers=auth_headers)
        assert resp.status_code == 422

    def test_list_projects(self, client, auth_headers):
        client.post("/api/projects/", json={"name": "P1"}, headers=auth_headers)
        client.post("/api/projects/", json={"name": "P2"}, headers=auth_headers)
        resp = client.get("/api/projects/", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.get_json()) == 2

    def test_get_project(self, client, auth_headers, project):
        resp = client.get(f"/api/projects/{project.id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["id"] == project.id

    def test_get_nonexistent_project(self, client, auth_headers):
        resp = client.get("/api/projects/99999", headers=auth_headers)
        assert resp.status_code == 404

    def test_update_project(self, client, auth_headers, project):
        resp = client.put(
            f"/api/projects/{project.id}",
            json={"name": "Renamed Project"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "Renamed Project"

    def test_delete_project(self, client, auth_headers, project):
        resp = client.delete(f"/api/projects/{project.id}", headers=auth_headers)
        assert resp.status_code == 200
        assert client.get(f"/api/projects/{project.id}", headers=auth_headers).status_code == 404

    def test_unauthenticated_access_denied(self, client):
        resp = client.get("/api/projects/")
        assert resp.status_code == 401

    def test_cannot_access_other_users_project(self, client, db, project):
        from app.models.user import User
        other = User(email="other@example.com", name="Other")
        other.set_password("password123")
        db.session.add(other)
        db.session.commit()

        login_resp = client.post("/api/auth/login", json={"email": "other@example.com", "password": "password123"})
        other_token = login_resp.get_json()["token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}

        resp = client.get(f"/api/projects/{project.id}", headers=other_headers)
        assert resp.status_code == 403
