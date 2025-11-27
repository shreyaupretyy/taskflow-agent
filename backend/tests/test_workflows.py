"""Test workflow API endpoints."""
import pytest


def test_create_workflow(client, auth_headers):
    """Test creating a workflow."""
    response = client.post(
        "/api/workflows",
        json={
            "name": "Test Workflow",
            "description": "A test workflow",
            "workflow_data": {
                "nodes": [
                    {
                        "id": "trigger",
                        "type": "trigger",
                        "data": {"config": {}}
                    }
                ],
                "edges": []
            }
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Workflow"
    assert "id" in data


def test_get_workflows(client, auth_headers):
    """Test getting user workflows."""
    # Create a workflow first
    client.post(
        "/api/workflows",
        json={
            "name": "Test Workflow",
            "description": "A test workflow",
            "workflow_data": {"nodes": [], "edges": []}
        },
        headers=auth_headers
    )
    
    response = client.get("/api/workflows", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_workflow_by_id(client, auth_headers):
    """Test getting a specific workflow."""
    # Create a workflow
    create_response = client.post(
        "/api/workflows",
        json={
            "name": "Test Workflow",
            "description": "A test workflow",
            "workflow_data": {"nodes": [], "edges": []}
        },
        headers=auth_headers
    )
    workflow_id = create_response.json()["id"]
    
    response = client.get(f"/api/workflows/{workflow_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == workflow_id


def test_update_workflow(client, auth_headers):
    """Test updating a workflow."""
    # Create a workflow
    create_response = client.post(
        "/api/workflows",
        json={
            "name": "Test Workflow",
            "description": "A test workflow",
            "workflow_data": {"nodes": [], "edges": []}
        },
        headers=auth_headers
    )
    workflow_id = create_response.json()["id"]
    
    # Update it
    response = client.put(
        f"/api/workflows/{workflow_id}",
        json={
            "name": "Updated Workflow",
            "description": "Updated description"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Workflow"


def test_delete_workflow(client, auth_headers):
    """Test deleting a workflow."""
    # Create a workflow
    create_response = client.post(
        "/api/workflows",
        json={
            "name": "Test Workflow",
            "description": "A test workflow",
            "workflow_data": {"nodes": [], "edges": []}
        },
        headers=auth_headers
    )
    workflow_id = create_response.json()["id"]
    
    # Delete it
    response = client.delete(f"/api/workflows/{workflow_id}", headers=auth_headers)
    assert response.status_code == 200
    
    # Verify it's deleted
    get_response = client.get(f"/api/workflows/{workflow_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_unauthorized_workflow_access(client):
    """Test accessing workflows without authentication."""
    response = client.get("/api/workflows")
    assert response.status_code == 401
