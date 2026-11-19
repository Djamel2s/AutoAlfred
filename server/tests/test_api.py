def test_health(client):
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert "ask_human" in body["agent_tools"] and "sim_reset" not in body["agent_tools"]


def test_initial_harness_version_exists(client):
    versions = client.get("/harness-versions").json()
    assert len(versions) == 1 and versions[0]["number"] == 1


def test_new_target_uses_initial_version(client, target):
    v1 = client.get("/harness-versions").json()[0]
    assert target["active_harness_version_id"] == v1["id"]


def test_duplicate_target_name(client, target):
    res = client.post("/targets", json={"name": "sim-ainex", "kind": "simulator", "mcp_url": "stub://ainex"})
    assert res.status_code == 409


def test_target_status_online_with_robot_sheet(client, target):
    status = client.get(f"/targets/{target['id']}/status").json()
    assert status["state"] == "online"
    assert status["info"]["profile"] == "ainex" and status["info"]["limits"]


def test_target_status_offline(client):
    t = client.post("/targets", json={"name": "robot", "kind": "physical", "mcp_url": "http://nowhere"}).json()
    status = client.get(f"/targets/{t['id']}/status").json()
    assert status["state"] == "offline" and status["error"]


def test_target_tools_mark_agent_visibility(client, target):
    tools = {t["name"]: t for t in client.get(f"/targets/{target['id']}/tools").json()}
    assert tools["pick"]["agent_visible"] is True
    assert tools["sim_state"]["agent_visible"] is False
    assert tools["pick"]["input_schema"]["required"] == ["object_id"]


def test_harness_versions_diff_and_rollback(client, target):
    v1 = client.get("/harness-versions").json()[0]
    config = {**v1["config"], "recovery_rules": v1["config"]["recovery_rules"] + ["Lire de près les petits textes."]}
    config["prompts"] = {**config["prompts"], "planner": "Nouveau prompt"}
    res = client.post(
        "/harness-versions",
        json={"label": "v2", "parent_id": v1["id"], "config": config, "rationale": "échecs de lecture"},
    )
    assert res.status_code == 201
    v2 = res.json()
    assert v2["number"] == 2 and v2["parent_id"] == v1["id"]

    changes = {c["path"]: c for c in client.get(f"/harness-versions/{v1['id']}/diff/{v2['id']}").json()["changes"]}
    assert set(changes) == {"prompts.planner", "recovery_rules"}

    t = client.post(f"/targets/{target['id']}/activate", json={"harness_version_id": v2["id"]}).json()
    assert t["active_harness_version_id"] == v2["id"]
    t = client.post(f"/targets/{target['id']}/activate", json={"harness_version_id": v1["id"]}).json()
    assert t["active_harness_version_id"] == v1["id"]


def test_harness_versions_are_immutable(client):
    v1 = client.get("/harness-versions").json()[0]
    assert client.put(f"/harness-versions/{v1['id']}", json={}).status_code == 405
    assert client.delete(f"/harness-versions/{v1['id']}").status_code == 405


def test_mission_lifecycle(client, target):
    res = client.post("/missions", json={"instruction": "Range la balle", "target_id": target["id"], "scenario": "ranger"})
    assert res.status_code == 201
    m = res.json()
    assert m["status"] == "pending" and m["harness_version_id"] == target["active_harness_version_id"]

    assert [x["id"] for x in client.get("/missions", params={"status": "pending"}).json()] == [m["id"]]
    assert client.get("/missions", params={"status": "failed"}).json() == []
    assert client.get(f"/missions/{m['id']}/events").json() == []

    assert client.post(f"/missions/{m['id']}/cancel").json()["status"] == "cancelled"
    assert client.post(f"/missions/{m['id']}/cancel").status_code == 409


def test_mission_unknown_target(client):
    assert client.post("/missions", json={"instruction": "x", "target_id": "nope"}).status_code == 404


def test_cannot_delete_target_with_missions(client, target):
    client.post("/missions", json={"instruction": "x", "target_id": target["id"]})
    assert client.delete(f"/targets/{target['id']}").status_code == 409
