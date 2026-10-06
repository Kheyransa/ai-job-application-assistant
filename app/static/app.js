"use strict";
const form = document.querySelector("#analysis-form");
const fields = ["resume", "job_description"];
const resultFields = ["matching_skills", "missing_skills", "relevant_experience", "strengths", "gaps", "cv_improvements", "interview_questions"];
const status = document.querySelector("#status");
const errorBanner = document.querySelector("#error");
const results = document.querySelector("#results");
let busy = false;
let submitted = false;
// Python str.strip includes these additional whitespace control characters.
const trimText = value => value.replace(/^[\u0009-\u000d\u001c-\u0020\u0085\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]+|[\u0009-\u000d\u001c-\u0020\u0085\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]+$/gu, "");
const count = value => Array.from(value).length;

function inputError(value) {
  const text = trimText(value);
  if (count(text) < 50) return "Enter at least 50 characters after trimming whitespace.";
  if (count(text) > 20000) return "Keep this text to 20,000 characters or fewer after trimming whitespace.";
  if ((text.match(/\p{L}/gu) || []).length < 20) return "Include meaningful text with at least 20 letters.";
  if (/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/u.test(text)) return "Remove unsupported control characters. Line breaks and tabs are allowed.";
  return "";
}

function refreshField(name, validate) {
  const field = document.getElementById(name);
  document.getElementById(`${name}-count`).textContent = `${count(trimText(field.value)).toLocaleString("en-US")} / 20,000`;
  if (!validate) return;
  const message = inputError(field.value);
  const error = document.getElementById(`${name}-error`);
  error.textContent = message;
  error.hidden = !message;
  field.setAttribute("aria-invalid", String(Boolean(message)));
}

function showError(message) {
  errorBanner.textContent = message;
  errorBanner.hidden = false;
  status.textContent = "";
}

function setBusy(value, label = "Analyzing match…") {
  busy = value;
  form.setAttribute("aria-busy", String(value));
  for (const id of ["analyze", "load-sample", "clear", ...fields]) document.getElementById(id).disabled = value;
  document.getElementById("spinner").hidden = !value;
  document.getElementById("analyze-arrow").hidden = value;
  document.getElementById("analyze-label").textContent = value ? label : "Analyze match";
}

function friendlyError(httpStatus, code) {
  if (httpStatus === 422) return "Please check both documents. Each needs 50–20,000 characters after trimming, at least 20 letters, and no unsupported control characters.";
  if (code === "invalid_ai_response") return "The AI returned an analysis in an unexpected format. Your inputs are preserved; you can try again.";
  if (code === "provider_network_error") return "The server could not reach the AI provider. Please try again later.";
  if (httpStatus === 504 || code === "provider_timeout") return "The AI provider took too long to respond. Your inputs are preserved; please try again later.";
  if (httpStatus === 503 && code === "ai_not_configured") return "Analysis is not configured on this server. Ask the app administrator to check the AI settings.";
  if (httpStatus === 502) return "The AI provider could not complete the analysis. Please try again later. Your inputs are preserved.";
  return "We couldn’t complete the analysis. Please try again later. Your inputs are preserved.";
}

function renderResults(data) {
  // Reject incomplete responses rather than rendering partial or fabricated results.
  if (!Number.isInteger(data.match_score) || data.match_score < 0 || data.match_score > 100 ||
      resultFields.some(name => !Array.isArray(data[name]) || data[name].some(item => typeof item !== "string"))) {
    throw new Error("invalid_response");
  }
  document.getElementById("score").textContent = String(data.match_score);
  for (const name of resultFields) {
    const container = document.getElementById(name);
    container.replaceChildren();
    const tags = container.classList.contains("tags");
    if (!data[name].length) {
      const empty = document.createElement(tags ? "p" : "li");
      empty.className = "empty";
      empty.textContent = "No items identified in the provided documents.";
      container.append(empty);
    } else {
      for (const text of data[name]) {
        const item = document.createElement(tags ? "span" : "li");
        if (tags) item.className = "tag";
        item.textContent = text;
        container.append(item);
      }
    }
  }
  results.hidden = false;
  status.textContent = "Analysis complete. Your match estimate and recommendations are ready.";
  document.getElementById("results-title").focus();
}

for (const name of fields) {
  document.getElementById(name).addEventListener("input", () => refreshField(name, submitted));
  document.getElementById(name).addEventListener("blur", () => refreshField(name, true));
}

form.addEventListener("submit", async event => {
  event.preventDefault();
  if (busy) return;
  submitted = true;
  errorBanner.hidden = true;
  results.hidden = true;
  fields.forEach(name => refreshField(name, true));
  const invalid = fields.find(name => inputError(document.getElementById(name).value));
  if (invalid) {
    showError("Please correct the highlighted fields before analyzing.");
    document.getElementById(invalid).focus();
    return;
  }
  setBusy(true);
  status.textContent = "Analyzing your documents. This may take a moment.";
  const payload = Object.fromEntries(fields.map(name => [name, trimText(document.getElementById(name).value)]));
  try {
    const response = await fetch("/api/v1/analyze", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload)});
    let data;
    try { data = await response.json(); } catch { data = null; }
    if (!response.ok) {
      showError(friendlyError(response.status, data?.code));
      return;
    }
    if (!data) throw new Error("invalid_response");
    renderResults(data);
  } catch (error) {
    showError(error instanceof TypeError ? "Couldn’t connect to the server. Check your connection and that the app is running. Your inputs are preserved." : "The server returned an unexpected response. Your inputs are preserved; please try again.");
  } finally { setBusy(false); }
});

document.getElementById("load-sample").addEventListener("click", async () => {
  if (busy) return;
  errorBanner.hidden = true;
  setBusy(true, "Loading sample…");
  status.textContent = "Loading fictional sample documents.";
  try {
    const response = await fetch("/ui/samples");
    if (!response.ok) throw new Error("sample_failure");
    const data = await response.json();
    if (fields.some(name => typeof data[name] !== "string")) throw new Error("sample_failure");
    results.hidden = true;
    submitted = false;
    for (const name of fields) {
      document.getElementById(name).value = data[name];
      refreshField(name, true);
    }
    status.textContent = "Fictional samples loaded. Select Analyze match to get a real analysis.";
  } catch { showError("Couldn’t load the sample documents. Your existing inputs are preserved."); }
  finally { setBusy(false); }
});

document.getElementById("clear").addEventListener("click", () => {
  if (busy) return;
  form.reset();
  submitted = false;
  results.hidden = true;
  errorBanner.hidden = true;
  for (const name of fields) {
    refreshField(name, false);
    document.getElementById(`${name}-error`).hidden = true;
    document.getElementById(name).removeAttribute("aria-invalid");
  }
  status.textContent = "Documents and results cleared.";
  document.getElementById("resume").focus();
});
