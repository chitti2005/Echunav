# public_app.py
import sqlite3
from flask import Flask, render_template, jsonify, redirect, url_for


app = Flask(__name__, static_folder="static", template_folder="templates")
DB_PATH = "database.db"



# ----------------------------------------------------------
# DB Connection
# ----------------------------------------------------------
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ----------------------------------------------------------
# Convert SQLite Row → dict
# ----------------------------------------------------------
def row_to_dict(row):
    return {key: row[key] for key in row.keys()}


# ----------------------------------------------------------
# Generate FULL image URL for public display
# ----------------------------------------------------------
def build_image_url(filename):
    if not filename:
        return None
    return url_for("static", filename=f"uploads/{filename}")


# ----------------------------------------------------------
# Home → redirect to live count
# ----------------------------------------------------------
@app.route("/")
def index():
    return redirect("/live_count")


# ----------------------------------------------------------
# LIVE COUNT HTML PAGE
# ----------------------------------------------------------
@app.route("/live_count")
def live_count():
    conn = db()

    candidates = conn.execute("SELECT * FROM candidates").fetchall()
    total_voters = conn.execute("SELECT COUNT(*) AS c FROM voters").fetchone()["c"]
    total_votes = conn.execute("SELECT COUNT(*) AS c FROM voters WHERE has_voted=1").fetchone()["c"]
    conn.close()

    # Convert Row → dict and attach usable image paths
    cand_list = []
    for c in candidates:
        d = row_to_dict(c)
        d["photo_url"] = build_image_url(c["photo"])
        d["symbol_url"] = build_image_url(c["symbol"])
        cand_list.append(d)

    # Compute max votes for "LEADING" badge
    max_votes = max([c["votes"] for c in cand_list]) if cand_list else 0

    return render_template(
        "public/live_count.html",
        candidates=cand_list,
        total_voters=total_voters,
        total_votes=total_votes,
        max_votes=max_votes
    )


# ----------------------------------------------------------
# JSON API (auto-refresh for AJAX)
# ----------------------------------------------------------
@app.route("/api/live_data")
def api_live_data():
    conn = db()

    candidates = conn.execute("SELECT * FROM candidates").fetchall()
    total_voters = conn.execute("SELECT COUNT(*) AS c FROM voters").fetchone()["c"]
    total_votes = conn.execute("SELECT COUNT(*) AS c FROM voters WHERE has_voted=1").fetchone()["c"]
    conn.close()

    # Convert rows → dict including full image URLs
    cand_list = []
    for c in candidates:
        d = row_to_dict(c)
        d["photo_url"] = build_image_url(c["photo"])
        d["symbol_url"] = build_image_url(c["symbol"])
        cand_list.append(d)

    return jsonify({
        "candidates": cand_list,
        "total_voters": total_voters,
        "total_votes": total_votes
    })


# ----------------------------------------------------------
# Run Server
# ----------------------------------------------------------
if __name__ == "__main__":
    app.run(port=5001, debug=True)
