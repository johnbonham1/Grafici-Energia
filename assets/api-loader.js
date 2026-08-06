(function () {
  const API_BY_HOST = {
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
})();
