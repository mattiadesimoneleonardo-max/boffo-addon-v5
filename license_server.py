"""
Einfacher Lizenz-Server für Boffo Addon / LicenseGate.java

Funktionsweise:
- Der Mod-Client ruft GET /verify?key=XXX&hwid=YYY auf.
- Dieser Server prüft, ob der Key existiert, noch gültig ist und ob er
  (optional) an genau diese Hardware-ID gebunden ist.
- Antwort ist NUR der nackte Text "OK" oder "DENY" (das erwartet
  LicenseGate.java so).

Starten:
    pip install flask
    python license_server.py
Läuft dann lokal auf http://127.0.0.1:5000

Für echten Einsatz im Internet brauchst du noch:
- Einen Server/VPS mit fester Adresse oder Domain
- HTTPS (z.B. über Caddy/Nginx als Reverse-Proxy, oder einen Dienst wie
  Render/Railway/Fly.io, die das automatisch machen)
- VERIFY_URL in LicenseGate.java auf diese Adresse anpassen
"""

from flask import Flask, request, jsonify
import json
import os
import datetime

app = Flask(__name__)

DB_FILE = "licenses.json"


def load_db():
    if not os.path.exists(DB_FILE):
        # Beispiel-Keys zum Ausprobieren. In echt würdest du hier
        # eigene Keys eintragen oder generieren.
        default = {
            "BOFFO-TEST-KEY-0001": {
                "owner": "dein-name",
                "hwid": None,          # None = noch nicht an ein Gerät gebunden
                "expires": None,       # None = läuft nie ab
                "active": True
            }
        }
        save_db(default)
        return default
    with open(DB_FILE, "r") as f:
        return json.load(f)


def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)


@app.route("/verify")
def verify():
    key = request.args.get("key", "").strip()
    hwid = request.args.get("hwid", "").strip()

    db = load_db()
    entry = db.get(key)

    if not entry:
        return "DENY", 200

    if not entry.get("active", False):
        return "DENY", 200

    expires = entry.get("expires")
    if expires:
        if datetime.datetime.utcnow() > datetime.datetime.fromisoformat(expires):
            return "DENY", 200

    # Erste Nutzung: Key an dieses Gerät binden.
    if entry.get("hwid") is None:
        entry["hwid"] = hwid
        db[key] = entry
        save_db(db)
        return "OK", 200

    # Spätere Nutzung: Gerät muss übereinstimmen.
    if entry["hwid"] != hwid:
        return "DENY", 200

    return "OK", 200


# Kleine Admin-Hilfsroute, um neue Keys zu erzeugen.
# WICHTIG: Für echten Einsatz unbedingt mit einem eigenen Passwort/Token
# absichern, sonst kann jeder im Internet neue Keys anlegen!
@app.route("/admin/add_key")
def add_key():
    admin_token = request.args.get("token", "")
    if admin_token != "HIER-EIGENES-ADMIN-PASSWORT-EINTRAGEN":
        return "forbidden", 403

    new_key = request.args.get("key", "").strip()
    owner = request.args.get("owner", "unbekannt")
    if not new_key:
        return "missing key", 400

    db = load_db()
    db[new_key] = {"owner": owner, "hwid": None, "expires": None, "active": True}
    save_db(db)
    return jsonify({"added": new_key, "owner": owner})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
