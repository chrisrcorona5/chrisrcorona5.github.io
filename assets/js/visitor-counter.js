/* Anonymous first-visit counter. No names, emails, fingerprints, or query strings. */
(function () {
  "use strict";
  var script = document.currentScript;
  if (!script || location.hostname !== "chrisrcorona5.github.io") return;
  var endpoint = script.dataset.endpoint;
  var visitor;
  try {
    if (localStorage.getItem("portfolio.exclude") === "1") return;
    if (navigator.globalPrivacyControl || navigator.doNotTrack === "1") return;
    visitor = localStorage.getItem("portfolio.visitor");
    if (!/^[0-9a-f-]{36}$/i.test(visitor || "")) {
      visitor = crypto.randomUUID();
      localStorage.setItem("portfolio.visitor", visitor);
    }
  } catch (_) {
    // Do not invent unstable identities when persistent storage is unavailable.
    return;
  }
  var sent = false;
  function send() {
    if (sent || document.visibilityState !== "visible") return;
    sent = true;
    fetch(endpoint + "/v1/visit", {
      method: "POST",
      mode: "cors",
      credentials: "omit",
      headers: { "Content-Type": "text/plain;charset=UTF-8" },
      body: JSON.stringify({ visitor: visitor }),
      keepalive: true
    }).catch(function () { /* Analytics must never interrupt the portfolio. */ });
    document.removeEventListener("visibilitychange", send);
  }
  // Link previews generally do not execute JS; wait for an actually visible page.
  if (document.visibilityState === "visible") setTimeout(send, 1200);
  else document.addEventListener("visibilitychange", send);
}());
