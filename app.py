from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

# Gemini API Key (keep secret!)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

from flask import Flask, render_template, request, jsonify
import subprocess
import json
import os

app = Flask(__name__)

NUCLEI_PATH = r"C:\nuclei\nuclei.exe"
TEMPLATE_PATH = "nuclei/templates"
OUTPUT_FILE = "scans/output.json"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/scan-page")
def scan_page():
    return render_template("scanning.html")


@app.route("/scan", methods=["POST"])
def scan():
    data = request.json
    target = data.get("url")

    if not target:
        return jsonify({"error": "No URL provided"}), 400

    # 🔥 IMPORTANT: reset output file every scan
    os.makedirs("scans", exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        pass  # truncate file

    command = [
        NUCLEI_PATH,
        "-u", target,
        "-t", TEMPLATE_PATH,
        "-jsonl",
        "-o", OUTPUT_FILE
    ]

    # 🔥 Capture output so subprocess never blocks
    subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )

    findings = []
    risk = 0

    # 🔥 Safely parse even if file is empty
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue

                item = json.loads(line)
                severity = item.get("info", {}).get("severity", "low")

                if severity == "high":
                    risk += 10
                elif severity == "medium":
                    risk += 5
                elif severity == "low":
                    risk += 2

                findings.append({
                    "name": item.get("info", {}).get("name", "Unknown issue"),
                    "severity": severity,
                    "description": item.get("info", {}).get("description", ""),
                    "matched_at": item.get("matched-at", "")
                })

    # 🔥 ALWAYS return a valid response
    return jsonify({
        "target": target,
        "risk": risk,
        "findings": findings,   # empty list is VALID
        "status": "completed"
    })



@app.route("/report")
def report():
    return render_template("report.html")


@app.route("/message", methods=["POST"])
def message():
    data = request.json
    user_msg = data.get("message", "").lower()
    scan = data.get("scan", {})

    findings = scan.get("findings", [])
    risk = scan.get("risk", 0)

    # Very simple rule-based logic (safe, demo-friendly)
    if "risk" in user_msg:
        reply = f"The overall risk score is {risk}/100. Higher scores indicate more severe or multiple vulnerabilities."

    elif "explain" in user_msg and findings:
        reply = (
            f"The scan detected {len(findings)} issue(s). "
            f"The most critical one is '{findings[0]['name']}', "
            f"which has a severity of {findings[0]['severity'].upper()}."
        )

    elif "fix" in user_msg:
        reply = (
            "Each issue can be fixed by validating inputs, sanitizing user data, "
            "and applying secure configuration best practices. "
            "I can guide you through a fix if needed."
        )

    elif not findings:
        reply = (
            "The scan completed successfully and no vulnerabilities were detected "
            "using the configured templates. This indicates a good security posture."
        )

    else:
        reply = (
            "I can explain vulnerabilities, assess risk, or suggest remediation steps. "
            "Try asking: 'Explain this issue' or 'How risky is this?'"
        )

    return jsonify({"reply": reply})

@app.route("/gemini", methods=["POST"])
def gemini():
    data = request.get_json()
    if not data or "contents" not in data:
        return jsonify({"error": "Missing contents for Gemini API"}), 400
    try:
        # The library expects 'contents' to be a list or a single string/list of parts
        # The frontend sends a structure compatible with the REST API.
        # We can extract the messages to pass to sendMessage or generate_content
        
        # Simple approach: Extract the last user message text to send distinct prompts
        # OR pass the full history if we want chat context.
        
        # Let's take the raw contents from the frontend
        # The library's model.generate_content(contents) works with properly formatted lists.
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=data["contents"]
        )
        
        # specific extraction for the text
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
