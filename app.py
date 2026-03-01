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
import time
import requests
from zapv2 import ZAPv2

app = Flask(__name__)

NUCLEI_PATH = r"C:\nuclei\nuclei.exe"
TEMPLATE_PATH = "nuclei/templates"
OUTPUT_FILE = "scans/output.json"

# ZAP Configuration
# IMPORTANT: Pull ZAP API key from .env file for security before pushing to Github
ZAP_API_KEY = os.getenv("ZAP_API_KEY", "7jjlbdanf2c14crshjj9nq5egt")
ZAP_PROXIES = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


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

    # 🔥 Nuclei command
    command = [
        NUCLEI_PATH,
        "-u", target,
        "-t", TEMPLATE_PATH,
        "-jsonl",
        "-o", OUTPUT_FILE
    ]

    # 🔥 Start Nuclei
    print(f"[*] Starting Nuclei Scan on {target}...")
    subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False
    )

    # 🔥 Start ZAP Scan integration
    zap_alerts = []
    print(f"[*] Starting OWASP ZAP Scan on {target}...")
    try:
        zap = ZAPv2(apikey=ZAP_API_KEY, proxies=ZAP_PROXIES)
        
        # Access target
        zap.urlopen(target)
        time.sleep(2)

        # Quick Spider
        print("[*] ZAP Spidering...")
        scan_id = zap.spider.scan(target)
        # Give spider a few seconds
        time.sleep(3) 

        # Quick Active Scan (Will take time depending on target)
        print("[*] ZAP Active Scanning...")
        scan_id = zap.ascan.scan(target)
        
        # Wait max 15 seconds for ZAP to avoid hanging the UI too long
        timeout = 15
        start_time = time.time()
        while int(zap.ascan.status(scan_id)) < 100:
            if time.time() - start_time > timeout:
                print("[!] ZAP Active Scan Timeout reached (Continuing with partial results)")
                break
            time.sleep(2)

        print("[*] ZAP Scan Complete. Fetching alerts...")
        # Get unique alerts for the target
        raw_alerts = zap.core.alerts(baseurl=target)
        
        # Format ZAP alerts to match Nuclei's frontend expectation
        for alert in raw_alerts:
            severity = alert.get('risk', 'Low').lower()
            if severity == 'informational': severity = 'low'
            
            zap_alerts.append({
                "name": f"[ZAP] {alert.get('name', 'Unknown')}",
                "severity": severity,
                "description": alert.get('description', ''),
                "matched_at": alert.get('url', target)
            })
    except Exception as e:
        print(f"[!] Error contacting ZAP Daemon: {e}")
        print("[!] Ensure ZAP is running on port 8080 and API key is correct. Continuing with Nuclei.")

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

    # 🔥 Combine ZAP findings with Nuclei findings
    findings.extend(zap_alerts)
    
    # Recalculate combined risk for newly added ZAP alerts
    for alert in zap_alerts:
        if alert['severity'] == "high":
            risk += 10
        elif alert['severity'] == "medium":
            risk += 5
        elif alert['severity'] == "low":
            risk += 2

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
        # Extract the raw text from the frontend's REST-formatted payload
        # payload structure: { contents: [ { role: "user", parts: [ { text: "..." } ] } ] }
        user_text = data["contents"][0]["parts"][0]["text"]
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=user_text
        )
        
        return jsonify({"reply": response.text})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
