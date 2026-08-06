(function () {
  const API_BY_HOST = {
    "dashboard-aeif.onrender.com": "https://dashboard-aeif-api.onrender.com",
    "johnbonham1.github.io": "https://dashboard-aeif-api.onrender.com",
    "dashboard-aeif-preprod.onrender.com": "https://dashboard-aeif-api-preprod.onrender.com",
    "dashboard-aeif-preproduzione.onrender.com": "https://dashboard-aeif-api-preprod.onrender.com",
  };

  window.AEIF_API_BASE = window.AEIF_API_BASE || API_BY_HOST[window.location.hostname] || "";

  window.loadAeifPayload = function loadAeifPayload(key) {
    if (!window.AEIF_API_BASE) return null;
    try {
      const request = new XMLHttpRequest();
      request.open("GET", window.AEIF_API_BASE + "/api/payloads/" + encodeURIComponent(key), false);
      request.send(null);
      if (request.status < 200 || request.status >= 300) return null;
      return JSON.parse(request.responseText).payload;
    } catch (_) {
      return null;
    }
  };

  window.requireAeifPayload = function requireAeifPayload(key) {
    const payload = window.loadAeifPayload(key);
    if (payload) return payload;

    const showMessage = function showMessage() {
      const target = document.querySelector(".wrap") || document.body;
      const message = document.createElement("div");
      message.style.cssText = [
        "margin:24px auto",
        "max-width:960px",
        "padding:18px 20px",
        "border:1px solid #d5dbe1",
        "border-radius:8px",
        "background:#fff7ed",
        "color:#1a2230",
        "font:600 15px -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif",
      ].join(";");
      message.textContent = "Dati temporaneamente non disponibili. Riprova tra poco.";
      target.prepend(message);
    };

    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", showMessage, { once: true });
    } else {
      showMessage();
    }

    throw new Error("Missing API payload: " + key);
  };
})();
