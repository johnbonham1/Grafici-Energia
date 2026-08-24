(function () {
  const VERSION = "v2026.08.25";
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
    @media(max-width:680px){
      .aeif-env-ribbon{font-size:10px;padding:7px 12px}
      .aeif-deploy-meta{text-align:left;padding:8px 14px 0}
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
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", install);
  } else {
    install();
  }
})();
