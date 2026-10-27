import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "nlp_engine" in data


def test_demo_endpoint():
    response = client.get("/api/demo")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "changes" in data
    assert len(data["changes"]) > 0
    assert data["summary"]["total_changes"] > 0

    comparison_id = data["id"]

    # Test retrieval of this comparison
    get_res = client.get(f"/api/comparisons/{comparison_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == comparison_id

    # Test PDF report export
    pdf_res = client.get(f"/api/comparisons/{comparison_id}/report/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 1000

    # Test CSV report export
    csv_res = client.get(f"/api/comparisons/{comparison_id}/report/csv")
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers["content-type"]
    assert "Change ID" in csv_res.text

    # Test review status toggle
    first_change = data["changes"][0]
    patch_res = client.patch(
        f"/api/changes/{first_change['id']}/review",
        json={"is_reviewed": True},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["is_reviewed"] is True


def test_compare_endpoint_upload():
    old_content = b"Section 1: Rules\nStudents must attend 75% of classes.\n"
    new_content = b"Section 1: Rules\nStudents must attend 80% of classes.\n"

    files = {
        "old_file": ("policy_2025.txt", old_content, "text/plain"),
        "new_file": ("policy_2026.txt", new_content, "text/plain"),
    }
    data = {
        "title": "API Test Comparison",
        "institution": "Test Dept",
        "old_version": "v1",
        "new_version": "v2",
    }

    response = client.post("/api/compare", files=files, data=data)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["title"] == "API Test Comparison"
    assert res_data["summary"]["modified_count"] >= 1


def test_invalid_file_extension():
    files = {
        "old_file": ("file.exe", b"invalid", "application/octet-stream"),
        "new_file": ("file.txt", b"valid", "text/plain"),
    }
    response = client.post("/api/compare", files=files)
    assert response.status_code == 400
    assert "unsupported" in response.json()["detail"].lower()
