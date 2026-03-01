<div align="center">
  <img src="https://raw.githubusercontent.com/zaproxy/zaproxy/main/src/images/zap32x32.png" alt="ZAP Logo" width="40" height="40" />
  <h1>Project Nucleus ⚡</h1>
  <p><b>An AI-Powered Web Vulnerability Scanner powered by Nuclei, OWASP ZAP, & Gemini 2.0</b></p>
</div>

---

Nucleus is a lightweight, high-performance web security scanner designed for penetration testers and developers. It fuses the rapid template-based scanning of **ProjectDiscovery's Nuclei** with the aggressive active fuzzing capabilities of **OWASP ZAP**. 

To make sense of the noise, Nucleus integrates **Google Gemini 2.0 Flash** directly into the reporting dashboard. Gemini acts as your personal AppSec engineer—analyzing findings, providing OWASP-aligned mitigation strategies, and answering questions about your target's risk posture.

### 🔥 Features

*   **Dual-Engine Scanning**: Runs both `nuclei` and `OWASP ZAP` asynchronously.
*   **Active Spidering & Fuzzing**: ZAP is programmatically orchestrated to crawl and attack endpoints.
*   **Custom Nuclei Templates**: Comes bundled with custom templates for catching low-hanging fruit (Local File Inclusion, Open Redirects, Reflected XSS).
*   **AI Chatbot Assistant**: Chat naturally with your scan results. Gemini maps findings to the OWASP Top 10 and gives concrete remediation advice.
*   **Beautiful UI**: A dark-mode, responsive TailwindCSS frontend interface.

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed on your system:

1.  **Python 3.9+**
2.  **Nuclei**: Download the `nuclei.exe` binary and place it in `C:\nuclei\nuclei.exe` (or update `NUCLEI_PATH` in `app.py`).
3.  **OWASP ZAP**: Download and install the [ZAP Desktop Client](https://www.zaproxy.org/download/).
4.  **Google Gemini API Key**: Grab a free key from [Google AI Studio](https://aistudio.google.com/).

---

## 🚀 Installation & Setup

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/nucleus-webscanner.git
cd nucleus-webscanner
```

**2. Create a virtual environment**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure Environment Variables**
Create a `.env` file in the root directory and add your Gemini API Key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
ZAP_API_KEY=your_zap_api_key_here
```
*(To find your ZAP API Key, open ZAP and go to Tools > Options > API)*

---

## 🕹️ Usage

**1. Start the OWASP ZAP Daemon**
Open the ZAP desktop application. Ensure it is listening on port `8080`. 

**2. Start the Backend Server**
```bash
python app.py
```

**3. Run a Scan**
*   Open your browser to `http://127.0.0.1:5000`
*   Enter a target URL (e.g., `http://testphp.vulnweb.com/`)
*   Wait for the scan to finish. The backend will orchestrate Nuclei and ZAP, merge the JSON findings, and calculate a risk score.
*   Once finished, you will be redirected to the **AI Reporting Dashboard** where you can ask Gemini to explain the vulnerabilities and how to fix them!

---

## ⚙️ Architecture

*   **Frontend**: HTML, vanilla JavaScript, TailwindCSS, Marked.js (for rendering AI markdown).
*   **Backend**: Python Flask.
*   **Engines**: 
    *   `subprocess` pipeline for Nuclei.
    *   `zapv2` Python SDK client for OWASP ZAP remote control.
    *   `google-genai` SDK for Gemini 2.0 Flash integration.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to fork this project, modify the Nuclei templates in `/nuclei/templates`, and submit a Pull Request.

---
*Disclaimer: This tool is intended for educational purposes and authorized penetration testing only. Do not scan targets you do not own or have explicit permission to test.*
