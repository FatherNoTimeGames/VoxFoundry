/* Disposable same-origin POC client. It is not a Sites SDK adapter. */
let csrf = "";
let pending = null;
const status = document.getElementById("status");
const error = document.getElementById("error");
function failure(exc) {
  error.textContent = exc.message;
  error.hidden = false;
}
async function api(path, options = {}) {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  if (csrf) headers.set("X-VF-CSRF", csrf);
  const response = await fetch(path, { ...options, headers });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(
      typeof body.detail === "string"
        ? body.detail
        : `Request failed (${response.status})`,
    );
  }
  return response.json();
}
async function refresh() {
  const jobs = await api("/api/jobs");
  const list = document.getElementById("jobs");
  list.replaceChildren();
  for (const job of jobs) {
    const item = document.createElement("li");
    const heading = document.createElement("h3");
    heading.textContent = job.text;
    const progress = document.createElement("p");
    progress.textContent = `${job.state} · ${job.progress}% · attempts ${job.attempts}`;
    item.append(heading, progress);
    if (job.error) {
      const message = document.createElement("p");
      message.textContent = job.error;
      item.append(message);
    }
    if (job.state === "failed") {
      const retry = document.createElement("button");
      retry.textContent = "Retry failed job";
      retry.onclick = async () => {
        retry.disabled = true;
        try {
          await api(`/api/jobs/${job.id}/retry`, { method: "POST" });
          await refresh();
        } catch (exc) {
          failure(exc);
          retry.disabled = false;
        }
      };
      item.append(retry);
    }
    if (job.state === "succeeded") {
      const audio = document.createElement("audio");
      audio.controls = true;
      audio.preload = "metadata";
      audio.src = `/api/jobs/${job.id}/audio`;
      audio.setAttribute("aria-label", "Completed test audio");
      const play = document.createElement("button");
      play.textContent = "Play test audio";
      play.onclick = async () => {
        try {
          await audio.play();
        } catch (exc) {
          failure(exc);
        }
      };
      const download = document.createElement("a");
      download.href = `/api/jobs/${job.id}/audio?download=true`;
      download.download = "voxfoundry-test.wav";
      download.textContent = "Download test audio";
      item.append(audio, play, download);
    }
    list.append(item);
  }
  const worker = await api("/api/worker-contact");
  document.getElementById("worker-contact").textContent =
    worker.seconds_since_contact === null
      ? "No worker contact yet."
      : `Last worker contact: ${Math.floor(worker.seconds_since_contact)} seconds ago. This does not prove it is still connected.`;
}
document.getElementById("request").onsubmit = async (event) => {
  event.preventDefault();
  error.hidden = true;
  const text = document.getElementById("text").value;
  const approved = document.getElementById("approved").checked;
  if (!approved) return;
  if (pending && pending.text !== text) {
    failure(
      new Error("Resolve the pending request before changing its passage."),
    );
    return;
  }
  pending = pending || {
    request_id: crypto.randomUUID(),
    text,
    approved: true,
  };
  document.getElementById("pending").hidden = false;
  document.getElementById("submit").disabled = true;
  try {
    await api("/api/jobs", { method: "POST", body: JSON.stringify(pending) });
    pending = null;
    document.getElementById("pending").hidden = true;
    status.textContent =
      "Job stored. Start the separate test worker, then refresh.";
    await refresh();
  } catch (exc) {
    failure(exc);
  } finally {
    document.getElementById("submit").disabled = false;
  }
};
document.getElementById("refresh").onclick = () => refresh().catch(failure);
(async () => {
  try {
    const token = new URLSearchParams(location.hash.slice(1)).get("token");
    history.replaceState(null, "", location.pathname);
    const session = token
      ? await api("/api/session", {
          method: "POST",
          body: JSON.stringify({ token }),
        })
      : await api("/api/session");
    csrf = session.csrf;
    document.getElementById("submit").disabled = false;
    document.getElementById("refresh").disabled = false;
    status.textContent =
      "Connected to a local disposable queue. No Site is deployed.";
    await refresh();
  } catch (exc) {
    failure(exc);
    status.textContent = "Open this POC through its launcher.";
  }
})();
