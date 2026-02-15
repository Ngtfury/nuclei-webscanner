// ---------- START SCAN ----------
function startScan() {
  const urlInput = document.getElementById("url");
  if (!urlInput || !urlInput.value.trim()) {
    alert("Please enter a URL");
    return;
  }

  const url = urlInput.value.trim();

  // Save target
  localStorage.setItem("scanTarget", url);
  localStorage.removeItem("scanResult");

  // Just redirect — DO NOT fetch here
  window.location.href = "/scan-page";
}



// ---------- REPORT PAGE RENDER ----------
document.addEventListener("DOMContentLoaded", () => {
  if (window.location.pathname !== "/report") return;

  const dataRaw = localStorage.getItem("scanResult");

  if (!dataRaw) {
    // Absolute fallback
    document.getElementById("report").innerHTML = `
      <div class="card low">
        <h4>No scan data available</h4>
        <p>The scan completed, but no findings were returned.</p>
      </div>
    `;
    return;
  }

  const data = JSON.parse(dataRaw);

  document.getElementById("scanned-url").innerText =
    "Scanned: " + data.target;

  let html = `<h3>Risk Score: ${data.risk}</h3>`;

  // 🔥 THIS IS THE IMPORTANT PART
  if (!data.findings || data.findings.length === 0) {
    html += `
      <div class="card low">
        <h4>No security issues found</h4>
        <p>
          The scan completed successfully and did not detect any
          matching vulnerabilities using the configured templates.
        </p>
      </div>
    `;
  } else {
    data.findings.forEach(f => {
      html += `
        <div class="card ${f.severity}">
          <h4>${f.name}</h4>
          <p>${f.description || "No description available."}</p>
          <small>Severity: ${f.severity.toUpperCase()}</small>
        </div>
      `;
    });
  }

  document.getElementById("report").innerHTML = html;
});


// ---------- CHATBOT (DUMMY) ----------
function sendMessage() {
  const input = document.getElementById("chat-input");
  if (!input || !input.value.trim()) return;

  const msg = input.value.trim();
  input.value = "";

  fetch("/message", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: msg })
  })
    .then(res => res.json())
    .then(data => {
      const chat = document.getElementById("chat");
      chat.innerHTML += `
        <p><b>You:</b> ${msg}</p>
        <p><b>Bot:</b> ${data.reply}</p>
      `;
      chat.scrollTop = chat.scrollHeight;
    });
}


// ---------- QUICK ACTION BUTTONS ----------
function quickAsk(text) {
  const input = document.getElementById("chat-input");
  input.value = text;
  sendMessage();
}


// ---------- SAFETY TIMEOUT ----------
setTimeout(() => {
  if (window.location.pathname === "/scan-page") {
    console.warn("Scan timeout fallback triggered");
    window.location.href = "/report";
  }
}, 30000);
