from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json, os, time

app = Flask(__name__)
CORS(app)

SCORES_FILE = "scores.json"
HTML_FILE = "bug_hunter.html"


def load_scores():
    if not os.path.exists(SCORES_FILE):
        return []
    with open(SCORES_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []


def save_scores(scores):
    with open(SCORES_FILE, "w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)


@app.route("/")
def index():
    scores = load_scores()
    scores.sort(key=lambda x: (-x.get("score", 0), x.get("avg_time", 999)))
    rows = ""
    for i, s in enumerate(scores[:20], 1):
        medal = ["🥇", "🥈", "🥉"][i - 1] if i <= 3 else f"#{i}"
        rows += (
            f"<tr><td>{medal}</td>"
            f"<td><b>{s['name']}</b></td>"
            f"<td>{s['score']}</td>"
            f"<td>{s['percent']}%</td>"
            f"<td>{s['avg_time']}s</td>"
            f"<td>{'🐍' if s['game'] == 'python' else '🎨'}</td></tr>"
        )
    empty = '<tr><td colspan="6" style="color:#3d5080;padding:20px 16px">Noch keine Einträge!</td></tr>'
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<title>🐜 Bug Hunter Leaderboard</title>
<style>
body{{font-family:monospace;background:#0d0f1a;color:#e2e6f3;padding:40px}}
h2{{color:#3d6fff;margin-bottom:20px;font-size:1.5rem}}
table{{border-collapse:collapse;width:100%;max-width:700px}}
th{{text-align:left;padding:8px 16px;color:#6b7280;font-size:.8rem;border-bottom:1px solid #252840}}
td{{padding:10px 16px;border-bottom:1px solid #1a1c2e}}
.btn{{color:#00d4aa;text-decoration:none;display:inline-block;margin-top:24px;border:1px solid #00d4aa;padding:10px 24px;border-radius:8px}}
</style></head>
<body>
<h2>🐜 Bug Hunter Leaderboard</h2>
<table>
<tr><th>#</th><th>Name</th><th>Score</th><th>%</th><th>Ø Zeit</th><th>Spiel</th></tr>
{rows if rows else empty}
</table>
<a class="btn" href="/game">🎮 Spiel öffnen</a>
</body></html>"""


@app.route("/game")
def serve_game():
    path = os.path.abspath(HTML_FILE)
    if os.path.exists(path):
        return send_file(path)
    return (
        f"<h2 style='font-family:monospace;color:#ff5555;padding:40px'>❌ {HTML_FILE} nicht gefunden!<br><code>{path}</code></h2>",
        404,
    )


@app.route("/api/scores", methods=["GET"])
def get_scores():
    scores = load_scores()
    scores.sort(key=lambda x: (-x.get("score", 0), x.get("avg_time", 999)))
    return jsonify(scores[:20])


@app.route("/api/scores", methods=["POST"])
def add_score():
    data = request.json
    if not data or not data.get("name"):
        return jsonify({"error": "name required"}), 400
    scores = load_scores()
    entry = {
        "name": data.get("name", "Anonym")[:20],
        "game": data.get("game", "python"),
        "mode": data.get("mode", "timer"),
        "score": int(data.get("score", 0)),
        "max_score": int(data.get("max_score", 1000)),
        "percent": round(
            data.get("score", 0) / max(data.get("max_score", 1000), 1) * 100, 1
        ),
        "levels_done": int(data.get("levels_done", 0)),
        "avg_time": round(float(data.get("avg_time", 0)), 1),
        "total_time": round(float(data.get("total_time", 0)), 1),
        "timestamp": int(time.time()),
    }
    scores.append(entry)
    save_scores(scores)
    scores.sort(key=lambda x: (-x.get("score", 0), x.get("avg_time", 999)))
    rank = next(
        (
            i + 1
            for i, s in enumerate(scores)
            if s["name"] == entry["name"] and s["timestamp"] == entry["timestamp"]
        ),
        len(scores),
    )
    return jsonify({"ok": True, "rank": rank, "total": len(scores)})


@app.route("/api/scores", methods=["DELETE"])
def clear_scores():
    save_scores([])
    return jsonify({"ok": True})


if __name__ == "__main__":
    print("\n🐜 Bug Hunter Server gestartet!")
    print("━" * 42)
    print(f"  🎮 Spiel:      http://localhost:5000/game")
    print(f"  🏆 Rangliste:  http://localhost:5000/")
    print(f"  📁 HTML:       {os.path.abspath(HTML_FILE)}")
    print("━" * 42)
    print("  Ctrl+C zum Beenden\n")
    app.run(debug=True, port=5000)
