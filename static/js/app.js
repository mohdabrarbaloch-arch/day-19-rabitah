/* Rabitah dashboard SPA — auth, link manager, analytics, settings. */
(() => {
  const API = "";
  let token = localStorage.getItem("rt_token") || "";
  let user = null;

  const $ = (id) => document.getElementById(id);

  async function api(path, opts = {}) {
    const headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = "Bearer " + token;
    const res = await fetch(API + path, { ...opts, headers });
    if (res.status === 204) return null;
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || "Request failed");
    return data;
  }

  function showError(msg) {
    const el = document.querySelector("#app-view .error");
    if (el) { el.textContent = msg; el.style.display = "block"; }
  }
  function hideError() {
    document.querySelectorAll("#app-view .error").forEach((el) => (el.style.display = "none"));
  }
  function showOk(id, msg) {
    const el = $(id);
    if (el) { el.textContent = msg; el.style.display = "block"; setTimeout(() => (el.style.display = "none"), 3000); }
  }

  function esc(s) {
    const d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  const authView = $("auth-view");
  const appView = $("app-view");

  function showAuth() { authView.classList.remove("hidden"); appView.classList.add("hidden"); }
  function showApp() { authView.classList.add("hidden"); appView.classList.remove("hidden"); }

  function setToken(t) {
    token = t;
    if (t) localStorage.setItem("rt_token", t);
    else localStorage.removeItem("rt_token");
  }

  async function loadMe() {
    try {
      user = await api("/api/auth/me");
      $("chip-name").textContent = user.display_name || user.username;
      $("my-url").textContent = "/" + user.username;
      $("my-url").href = "/" + user.username;
      $("set-name").value = user.display_name || "";
      $("set-bio").value = user.bio || "";
      $("set-avatar").value = user.avatar_url || "";
      $("set-theme").value = user.theme || "midnight";
      showApp();
      loadLinks();
    } catch (e) {
      setToken("");
      showAuth();
    }
  }

  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      const isLogin = tab.dataset.tab === "login";
      $("login-form").classList.toggle("hidden", !isLogin);
      $("register-form").classList.toggle("hidden", isLogin);
    });
  });

  $("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      const d = await api("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ email: $("login-email").value.trim(), password: $("login-pass").value }),
      });
      setToken(d.access_token);
      loadMe();
    } catch (err) { showError(err.message); }
  });

  $("register-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      const d = await api("/api/auth/register", {
        method: "POST",
        body: JSON.stringify({
          email: $("reg-email").value.trim(),
          username: $("reg-user").value.trim(),
          password: $("reg-pass").value,
        }),
      });
      setToken(d.access_token);
      loadMe();
    } catch (err) { showError(err.message); }
  });

  $("demo-login").addEventListener("click", async (e) => {
    e.preventDefault();
    try {
      const d = await api("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ email: "demo@rabitah.pk", password: "demo12345" }),
      });
      setToken(d.access_token);
      loadMe();
    } catch (err) { showError("Demo user not seeded. Run: python -m scripts.seed"); }
  });

  $("logout-btn").addEventListener("click", () => { setToken(""); showAuth(); });

  document.querySelectorAll(".nav-item[data-view]").forEach((item) => {
    item.addEventListener("click", () => {
      document.querySelectorAll(".nav-item[data-view]").forEach((i) => i.classList.remove("active"));
      item.classList.add("active");
      ["editor", "analytics", "settings"].forEach((v) => $("view-" + v).classList.toggle("hidden", v !== item.dataset.view));
      if (item.dataset.view === "analytics") loadAnalytics();
    });
  });

  $("view-page").addEventListener("click", () => {
    if (user) window.open("/" + user.username, "_blank");
  });

  async function loadLinks() {
    try {
      const links = await api("/api/links");
      renderLinks(links);
    } catch (e) { showError(e.message); }
  }

  function renderLinks(links) {
    const list = $("links-list");
    if (!links.length) {
      list.innerHTML = '<div class="empty">No links yet. Add your first one above 👆</div>';
      return;
    }
    list.innerHTML = links.map((l) => `
      <div class="link-row">
        <span class="title">${esc(l.title)}</span>
        <span class="url">${esc(l.url)}</span>
        <span class="clicks">👆 ${l.click_count}</span>
        <span class="badge ${l.is_active ? "on" : "off"}">${l.is_active ? "ON" : "OFF"}</span>
        <button class="icon-btn" data-act="toggle" data-id="${l.id}" title="Toggle">${l.is_active ? "🙈" : "👁️"}</button>
        <button class="icon-btn del" data-act="del" data-id="${l.id}" title="Delete">🗑️</button>
      </div>`).join("");
  }

  $("link-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    hideError();
    try {
      await api("/api/links", {
        method: "POST",
        body: JSON.stringify({
          title: $("link-title").value.trim(),
          url: $("link-url").value.trim(),
          icon: $("link-icon").value,
          sort_order: parseInt($("link-order").value || "0", 10),
          is_active: true,
        }),
      });
      $("link-form").reset();
      showOk("link-ok", "Link added! It's live on your page.");
      loadLinks();
    } catch (err) { showError(err.message); }
  });

  $("links-list").addEventListener("click", async (e) => {
    const btn = e.target.closest("[data-act]");
    if (!btn) return;
    const id = btn.dataset.id;
    try {
      if (btn.dataset.act === "del") {
        await api("/api/links/" + id, { method: "DELETE" });
      } else {
        await api("/api/links/" + id, { method: "PATCH", body: JSON.stringify({}) });
        const links = await api("/api/links");
        const link = links.find((l) => l.id === parseInt(id, 10));
        await api("/api/links/" + id, { method: "PATCH", body: JSON.stringify({ is_active: !link.is_active }) });
      }
      loadLinks();
    } catch (err) { showError(err.message); }
  });

  async function loadAnalytics() {
    try {
      const a = await api("/api/analytics?days=14");
      $("stat-total").textContent = a.total_clicks;
      $("stat-links").textContent = a.total_links;
      const today = a.daily.length ? a.daily[a.daily.length - 1].count : 0;
      $("stat-today").textContent = today;
      const max = Math.max(1, ...a.daily.map((d) => d.count));
      $("chart").innerHTML = a.daily.map((d) => `
        <div class="bar-col" title="${d.date}: ${d.count}">
          <div class="bar ${d.count === 0 ? "zero" : ""}" style="height:${Math.max(3, Math.round((d.count / max) * 110))}px"></div>
          <span class="bar-label">${d.date.slice(5)}</span>
        </div>`).join("");
      $("top-links").innerHTML = a.top_links.length
        ? a.top_links.map((l) => `
            <div class="link-row">
              <span class="title">${esc(l.title)}</span>
              <span class="url">${esc(l.url)}</span>
              <span class="clicks">👆 ${l.click_count}</span>
            </div>`).join("")
        : '<div class="empty">No clicks yet — share your page!</div>';
    } catch (e) { showError(e.message); }
  }

  $("settings-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    hideError();
    try {
      user = await api("/api/auth/me", {
        method: "PATCH",
        body: JSON.stringify({
          display_name: $("set-name").value.trim(),
          bio: $("set-bio").value.trim(),
          avatar_url: $("set-avatar").value.trim(),
          theme: $("set-theme").value,
        }),
      });
      $("chip-name").textContent = user.display_name || user.username;
      showOk("settings-ok", "Page updated!");
    } catch (err) { showError(err.message); }
  });

  if (token) loadMe();
  else showAuth();
})();
