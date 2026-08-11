(function () {
  const VERSION = "v2026.08.25.1";
  const DEPLOY_DATE = "25/08/2026";
  const host = window.location.hostname || "";
  const params = new URLSearchParams(window.location.search);
  const isPreprod = /preprod|preproduzione/i.test(host) || params.get("env") === "preprod";
  const envLabel = isPreprod ? "Pre-produzione" : "Produzione";

  const style = document.createElement("style");
  style.textContent = `
    .aeif-env-ribbon{
      width:100%;
      padding:8px 18px;
      background:#fff7e8;
      border-bottom:1px solid #ecd3a2;
      color:#735315;
      font:700 12px/1.4 'SF Mono',ui-monospace,Menlo,Consolas,monospace;
      letter-spacing:.08em;
      text-transform:uppercase;
      text-align:center;
    }
    .aeif-deploy-meta{
      max-width:1180px;
      margin:24px auto 8px;
      padding:10px 18px 0;
      color:#7b8898;
      font:600 11px/1.5 'SF Mono',ui-monospace,Menlo,Consolas,monospace;
      letter-spacing:.06em;
      text-transform:uppercase;
      text-align:right;
    }
    body.has-aeif-preprod-ribbon{padding-top:0}
    .aeif-mobile-nav{
      position:fixed;
      left:12px;
      right:12px;
      bottom:calc(12px + env(safe-area-inset-bottom, 0px));
      display:none;
      grid-template-columns:1fr 1fr;
      gap:8px;
      z-index:9999;
      pointer-events:none;
    }
    .aeif-mobile-nav button,
    .aeif-mobile-nav a{
      pointer-events:auto;
      display:flex;
      align-items:center;
      justify-content:center;
      min-height:42px;
      border:1px solid #cfd8e3;
      border-radius:11px;
      background:rgba(255,255,255,.94);
      color:#151d2a;
      text-decoration:none;
      font:750 13px/1 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
      box-shadow:0 10px 24px -18px rgba(20,30,45,.48),0 1px 5px rgba(20,30,45,.10);
      -webkit-backdrop-filter:blur(10px);
      backdrop-filter:blur(10px);
    }
    .aeif-mobile-nav button{appearance:none;-webkit-appearance:none;cursor:pointer}
    @media(max-width:680px){
      .aeif-env-ribbon{font-size:10px;padding:7px 12px}
      .aeif-deploy-meta{text-align:left;padding:8px 14px 0}
      body{padding-bottom:calc(72px + env(safe-area-inset-bottom, 0px))}
      .aeif-mobile-nav{display:grid}
    }
  `;

  function install() {
    document.head.appendChild(style);
    if (isPreprod) {
      document.body.classList.add("has-aeif-preprod-ribbon");
      const ribbon = document.createElement("div");
      ribbon.className = "aeif-env-ribbon";
      ribbon.textContent = "Ambiente di pre-produzione";
      document.body.insertBefore(ribbon, document.body.firstChild);
    }

    const footer = document.createElement("div");
    footer.className = "aeif-deploy-meta";
    footer.textContent = `${envLabel} · ${VERSION} · ultimo deploy ${DEPLOY_DATE}`;
    document.body.appendChild(footer);

    const nav = document.createElement("nav");
    nav.className = "aeif-mobile-nav";
    nav.setAttribute("aria-label", "Navigazione mobile");
    nav.innerHTML = `<button type="button" class="aeif-back">Indietro</button><a href="index.html">Home</a>`;
    nav.querySelector(".aeif-back").addEventListener("click", function () {
      if (window.history.length > 1) {
        window.history.back();
      } else {
        window.location.href = "index.html";
      }
    });
    document.body.appendChild(nav);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", install);
  } else {
    install();
  }
})();
