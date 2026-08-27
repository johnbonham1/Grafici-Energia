(function () {
  const API_BY_HOST = {
    "dashboard-aeif.onrender.com": "https://dashboard-aeif-api-f497.onrender.com",
    "johnbonham1.github.io": "https://dashboard-aeif-api-f497.onrender.com",
    "dashboard-aeif-preprod.onrender.com": "https://dashboard-aeif-api-preprod.onrender.com",
    "dashboard-aeif-preproduzione.onrender.com": "https://dashboard-aeif-api-preprod.onrender.com",
  };

  window.AEIF_API_BASE = window.AEIF_API_BASE || API_BY_HOST[window.location.hostname] || "";
  const CACHE_PREFIX = "aeif-data-cache-v2:";
  const FALLBACK_FILE_BY_KEY = {
    ets_cap_2005_2050: "assets/fallback-ets-cap-2005-2050.json",
  };
  let fallbackPayloads = null;

  function readCache(key) {
    try {
      const raw = window.localStorage && window.localStorage.getItem(CACHE_PREFIX + key);
      return raw ? JSON.parse(raw).value : null;
    } catch (_) {
      return null;
    }
  }

  function writeCache(key, value) {
    try {
      if (window.localStorage && value) {
        window.localStorage.setItem(CACHE_PREFIX + key, JSON.stringify({ value, savedAt: Date.now() }));
      }
    } catch (_) {}
  }

  function requestJson(url) {
    try {
      const request = new XMLHttpRequest();
      request.open("GET", url, false);
      request.send(null);
      if (request.status < 200 || request.status >= 300) return null;
      return JSON.parse(request.responseText);
    } catch (_) {
      return null;
    }
  }

  function loadFallbackPayload(key) {
    if (FALLBACK_FILE_BY_KEY[key]) {
      return requestJson(FALLBACK_FILE_BY_KEY[key]);
    }
    if (!fallbackPayloads) {
      fallbackPayloads = requestJson("assets/fallback-payloads.json") || {};
    }
    return fallbackPayloads[key] || null;
  }

  window.loadAeifPayload = function loadAeifPayload(key) {
    const cacheKey = "payload:" + key;
    if (window.AEIF_API_BASE) {
      const response = requestJson(window.AEIF_API_BASE + "/api/payloads/" + encodeURIComponent(key));
      if (response && response.payload) {
        writeCache(cacheKey, response.payload);
        return response.payload;
      }
    }
    return readCache(cacheKey) || loadFallbackPayload(key);
  };

  window.loadAeifSeries = function loadAeifSeries(key) {
    const cacheKey = "series:" + key;
    if (window.AEIF_API_BASE) {
      const response = requestJson(window.AEIF_API_BASE + "/api/series/" + encodeURIComponent(key));
      if (response) {
        writeCache(cacheKey, response);
        return response;
      }
    }
    return readCache(cacheKey);
  };

  window.loadAeifMonthlySeries = function loadAeifMonthlySeries(key) {
    const cacheKey = "series-monthly:" + key;
    if (window.AEIF_API_BASE) {
      const response = requestJson(window.AEIF_API_BASE + "/api/series/" + encodeURIComponent(key) + "/monthly");
      if (response) {
        writeCache(cacheKey, response);
        return response;
      }
    }
    return readCache(cacheKey);
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
