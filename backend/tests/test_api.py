from datetime import date, timedelta

from tests.conftest import login


def payload(title="Tarefa", days=2, priority="MEDIUM"):
    return {
        "title": title,
        "description": "Detalhes",
        "category": "Testes",
        "responsible": "Professor",
        "due_date": str(date.today() + timedelta(days=days)),
        "priority": priority,
        "status": "PENDING",
    }


def test_authentication_and_admin_crud(client):
    assert client.get("/api/auth/me").status_code == 401
    login(client)
    created = client.post("/api/tasks", json=payload()).json()
    assert created["title"] == "Tarefa"
    changed = client.patch(f"/api/tasks/{created['id']}", json={"status": "COMPLETED"})
    assert changed.json()["status"] == "COMPLETED"
    assert client.delete(f"/api/tasks/{created['id']}").status_code == 204


def test_member_cannot_mutate(client):
    login(client, "member@test.com")
    assert client.post("/api/tasks", json=payload()).status_code == 403


def test_filters_order_and_summary(client):
    login(client)
    client.post("/api/tasks", json=payload("Futura", 3, "LOW"))
    client.post("/api/tasks", json=payload("Atrasada", -2, "URGENT"))
    items = client.get("/api/tasks").json()["items"]
    assert items[0]["title"] == "Atrasada"
    assert client.get("/api/tasks?upcoming=true").json()["total"] == 1
    assert client.get("/api/tasks?overdue=true").json()["total"] == 1
    summary = client.get("/api/dashboard/summary").json()
    assert summary["pending_tasks"] == 2 and summary["overdue_tasks"] == 1
