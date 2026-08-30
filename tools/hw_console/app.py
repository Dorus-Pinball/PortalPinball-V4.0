"""Local web console for tracking hardware bring-up on Portal Pinball V4.0.

Run with:  python tools/hw_console/app.py
Then open: http://localhost:5000

See README.md in this directory for the intended workflow.
"""
from flask import Flask, jsonify, request

import registry

app = Flask(__name__)


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/boards")
def list_boards():
    data = registry.load_registry()
    return jsonify(data.get("boards", {}))


@app.patch("/api/boards/<board_id>")
def update_board(board_id):
    data = registry.load_registry()
    boards = data.get("boards", {})
    if board_id not in boards:
        return jsonify({"error": f"unknown board '{board_id}'"}), 404

    body = request.get_json(force=True) or {}
    if "status" in body:
        if body["status"] not in registry.VALID_BOARD_STATUSES:
            return jsonify({"error": f"status must be one of {registry.VALID_BOARD_STATUSES}"}), 400
        boards[board_id]["status"] = body["status"]

    registry.save_registry(data)
    return jsonify(boards[board_id])


@app.get("/api/components")
def list_components():
    data = registry.load_registry()
    components = data.get("components", {})
    status_filter = request.args.get("status")
    if status_filter:
        components = {k: v for k, v in components.items() if v.get("status") == status_filter}
    return jsonify(components)


@app.get("/api/components/<name>")
def get_component(name):
    data = registry.load_registry()
    component = (data.get("components") or {}).get(name)
    if component is None:
        return jsonify({"error": f"unknown component '{name}'"}), 404
    return jsonify(component)


@app.post("/api/components")
def add_component():
    body = request.get_json(force=True) or {}
    name = body.get("name", "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400

    data = registry.load_registry()
    components = data.setdefault("components", {})
    if name in components:
        return jsonify({"error": f"component '{name}' already exists"}), 409

    switches = body.get("switches", [])
    coils = body.get("coils", [])

    for entry in switches + coils:
        if not entry.get("name") or not entry.get("number"):
            return jsonify({"error": "every switch/coil entry needs a name and number"}), 400

    conflicts = []
    for entry in switches:
        conflict = registry.check_collision(data, "switches", entry["number"])
        if conflict:
            conflicts.append(conflict)
    for entry in coils:
        conflict = registry.check_collision(data, "coils", entry["number"])
        if conflict:
            conflicts.append(conflict)
    if conflicts:
        return jsonify({"error": "number collision", "conflicts": conflicts}), 409

    for entry in switches:
        entry.setdefault("status", "planned")
    for entry in coils:
        entry.setdefault("status", "planned")

    components[name] = {
        "display_name": body.get("display_name", name),
        "status": body.get("status", "planned"),
        "mpf_devices": body.get("mpf_devices", []),
        "switches": switches,
        "coils": coils,
        "checklist": registry.checklist_template(),
        "notes": body.get("notes", ""),
    }

    registry.save_registry(data)
    return jsonify(components[name]), 201


@app.patch("/api/components/<name>")
def update_component(name):
    data = registry.load_registry()
    components = data.get("components", {})
    if name not in components:
        return jsonify({"error": f"unknown component '{name}'"}), 404

    component = components[name]
    body = request.get_json(force=True) or {}

    if "status" in body:
        if body["status"] not in registry.VALID_COMPONENT_STATUSES:
            return jsonify({"error": f"status must be one of {registry.VALID_COMPONENT_STATUSES}"}), 400
        component["status"] = body["status"]

    if "notes" in body:
        component["notes"] = body["notes"]

    if "checklist" in body:
        component["checklist"] = body["checklist"]

    if "switch_status" in body:
        for entry in component.get("switches", []):
            if entry["name"] == body["switch_status"]["name"]:
                entry["status"] = body["switch_status"]["status"]

    if "coil_status" in body:
        for entry in component.get("coils", []):
            if entry["name"] == body["coil_status"]["name"]:
                entry["status"] = body["coil_status"]["status"]

    registry.save_registry(data)
    return jsonify(component)


if __name__ == "__main__":
    # use_reloader=False: the default reloader watches the whole app directory, including
    # data/components.yaml - since every PATCH/POST writes that file, the reloader would restart
    # the server on every single edit, breaking requests mid-flight.
    app.run(debug=True, port=5000, use_reloader=False)
