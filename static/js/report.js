// ---------- LOAD SCAN DATA ----------
const scanData = JSON.parse(localStorage.getItem("scanResult") || "{}");

// ---------- FILL SCAN SUMMARY ----------
document.addEventListener("DOMContentLoaded", () => {
  // Target URL
  const urlEl = document.querySelector("[data-target-url]");
  if (urlEl && scanData.target) {
    urlEl.textContent = scanData.target;
  }

  // Risk score
  const riskScore = scanData.risk || 0;
  const riskEl = document.querySelector("[data-risk-score]");
  if (riskEl) {
    riskEl.textContent = riskScore;
  }

  // Vulnerability count
  const vulnCountEl = document.querySelector("[data-vuln-count]");
  if (vulnCountEl) {
    vulnCountEl.textContent = scanData.findings?.length || 0;
  }

  // Populate vulnerabilities
  renderVulnerabilities();

  // Initial assistant message
  injectInitialMessage();

  // Add Enter key event for chat input
  const chatInput = document.getElementById("chat-input");
  if (chatInput) {
    chatInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        window.sendChatMessage();
      }
    });
  }
});


// ---------- RENDER VULNERABILITIES ----------
function renderVulnerabilities() {
  const container = document.getElementById("vuln-list");
  if (!container) return;

  container.innerHTML = "";

  const findings = scanData.findings || [];

  if (findings.length === 0) {
    container.innerHTML = `
      <div class="rounded-xl bg-surface-dark p-4 border border-[#422929]">
        <p class="text-green-400 text-sm font-bold">No security issues detected</p>
        <p class="text-[#c19a9a] text-xs mt-1">
          The scan completed successfully without detecting vulnerabilities.
        </p>
      </div>
    `;
    return;
  }

  findings.forEach(f => {
    const severityColor =
      f.severity === "high" ? "border-primary" :
        f.severity === "medium" ? "border-orange-500" :
          "border-blue-400";

    container.innerHTML += `
      <div class="rounded-xl bg-surface-dark border-l-4 ${severityColor} p-4 shadow-md border border-[#422929]">
        <h4 class="text-white font-bold text-sm">${f.name}</h4>
        <p class="text-[#c19a9a] text-xs mt-1">${f.description}</p>
        <code class="bg-[#1f1313] px-2 py-1 mt-2 inline-block rounded text-[10px] text-gray-400 font-mono">
          ${f.matched_at || "N/A"}
        </code>
      </div>
    `;
  });
}


// ---------- CHATBOT ----------
// Gemini API integration
const GEMINI_API_URL = "/gemini";

// Compose system prompt with scan context
function getSystemPrompt() {
  let prompt = "You are an expert Application Security Analyst and Penetration Tester. Your task is to analyze the results of a Web Application Vulnerability Scan and provide a professional report. ";
  if (scanData.target) {
    prompt += `The target application is: ${scanData.target}. `;
  }
  prompt += `The calculated risk score is ${scanData.risk || 0} out of 100. `;

  if (scanData.findings && scanData.findings.length > 0) {
    prompt += `You found ${scanData.findings.length} vulnerabilities from a combined AST pipeline (Nuclei templates + OWASP ZAP Active Fuzzing). Here are the raw findings:\n`;
    scanData.findings.forEach((f, i) => {
      prompt += `[Issue ${i + 1}] Name: ${f.name}, Severity: ${f.severity}, Description: ${f.description}, Matched at: ${f.matched_at}.\n`;
    });
    prompt += `\nINSTRUCTIONS: 
1. When summarizing or explaining these findings, you MUST map each issue to its corresponding OWASP Top 10 (2021) category if applicable (e.g., A01:Broken Access Control, A03:Injection).
2. Provide concrete mitigation strategies aligned with official OWASP best practices.
3. Be concise and format your response professionally.`;
  } else {
    prompt += "No vulnerabilities were detected using the current template set.";
  }
  return prompt;
}

window.sendChatMessage = async function (text = null) {
  const input = document.getElementById("chat-input");
  const message = text || (input ? input.value.trim() : "");
  if (!message) return;

  if (input) input.value = "";
  appendUserMessage(message);

  // Prepare Gemini API request
  const systemPrompt = getSystemPrompt();
  const payload = {
    contents: [
      {
        role: "user", parts: [
          { text: systemPrompt + "\nUser: " + message }
        ]
      }
    ]
  };

  try {
    const res = await fetch(GEMINI_API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    let reply = "Sorry, I couldn't get a response.";

    if (data && data.reply) {
      reply = data.reply;
    } else if (data && data.error) {
      reply = `[Gemini error] ${data.error}`;
    }

    appendBotMessage(reply);
  } catch (e) {
    appendBotMessage("[Error contacting Gemini API]");
  }
}


// ---------- UI MESSAGE HELPERS ----------
function appendUserMessage(text) {
  const chat = document.querySelector(".chat-scroll-fade");
  if (!chat) return;
  chat.innerHTML += `
    <div class="self-end bg-[#2f1d1d] p-4 rounded-2xl rounded-tr-sm text-white max-w-[70%]">
      ${text}
    </div>
  `;
  chat.scrollTop = chat.scrollHeight;
}

function appendBotMessage(text) {
  const chat = document.querySelector(".chat-scroll-fade");
  if (!chat) return;

  // Parse markdown if available
  const formattedText = typeof marked !== 'undefined' ? marked.parse(text) : text;

  chat.innerHTML += `
    <div class="self-start bg-[#0f0f0f] border border-[#2f1d1d] p-5 rounded-2xl rounded-tl-sm text-gray-200 w-full max-w-[85%] prose prose-invert prose-p:leading-relaxed prose-pre:bg-[#1a1010] prose-pre:border prose-pre:border-[#422929]">
      ${formattedText}
    </div>
  `;
  chat.scrollTop = chat.scrollHeight;
}


// ---------- INITIAL BOT MESSAGE ----------
function injectInitialMessage() {
  const findings = scanData.findings || [];
  let intro;

  if (findings.length === 0) {
    intro = "The scan completed successfully and no vulnerabilities were detected.";
  } else {
    intro = `The scan detected ${findings.length} issue(s). I can help explain them or suggest fixes.`;
  }

  appendBotMessage(intro);
}


// ---------- QUICK ACTION BUTTONS ----------
window.quickAsk = function (text) {
  window.sendChatMessage(text);
}
