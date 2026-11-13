/* Revexa API endpoint configuration.
   Local development uses FastAPI on port 8000.
   Before deployment, replace the production URL with your Render service URL.
*/
(() => {
  const host = window.location.hostname;
  const isLocal = host === "localhost" || host === "127.0.0.1";
  const configuredProductionUrl = "https://revexa-uax0.onrender.com";
  window.REVEXA_API_BASE_URL = window.REVEXA_API_BASE_URL ||
    (isLocal ? "http://127.0.0.1:8000" : configuredProductionUrl);
})();
