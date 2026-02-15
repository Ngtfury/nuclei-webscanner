# AI Web Vulnerability Scanner

A minimal web vulnerability scanner using [Nuclei](https://github.com/projectdiscovery/nuclei) and Google Gemini AI to analyze reports.

## Prerequisites
1. **Python 3.8+**
2. **Nuclei** installed and added to PATH (or at `C:\nuclei\nuclei.exe`).
   - [Install Nuclei](https://github.com/projectdiscovery/nuclei#install-nuclei)

## Installation

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the root directory (already created) with your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

3. Ensure `nuclei` templates are available in the `nuclei/templates` folder.

## Running the App

1. Start the Flask server:
   ```bash
   python app.py
   ```
2. Open your browser at: `http://127.0.0.1:5000`

## Usage
- Enter a target URL (e.g., `http://testphp.vulnweb.com`).
- Wait for the scan to complete.
- View the report and chat with the AI assistant to understand vulnerabilities and fixes.
