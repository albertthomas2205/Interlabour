(function () {
    "use strict";

    // Auto-load helper scripts (NL/EN toggle on every page + dynamic jobs on home page)
    (function loadAuxScripts() {
        function inject(src, attr) {
            try {
                if (document.querySelector('script[' + attr + ']')) return;
                var s = document.createElement("script");
                s.src = src;
                s.async = true;
                s.setAttribute(attr, "1");
                (document.head || document.body || document.documentElement).appendChild(s);
            } catch (_e) {}
        }
        inject("/assets/js/i18n.js", "data-i18n-loader");
        inject("/assets/js/dynamic-jobs.js?v=3", "data-dyn-jobs-loader");
        inject("/assets/js/dynamic-services.js?v=13", "data-dyn-services-loader");
        inject("/assets/js/dynamic-blog.js", "data-dyn-blog-loader");
        inject("/assets/js/dynamic-home.js", "data-dyn-home-loader");
    })();

    // Auto-load the site-wide responsive overrides stylesheet on every page.
    // Synchronous injection so the rules apply on first paint and we don't
    // see a flash of unstyled mobile layout.
    (function loadResponsiveCSS() {
        try {
            if (document.querySelector('link[data-responsive-overrides]')) return;
            var link = document.createElement("link");
            link.rel = "stylesheet";
            link.href = "/assets/css/responsive-overrides.css?v=13";
            link.setAttribute("data-responsive-overrides", "1");
            (document.head || document.documentElement).appendChild(link);
        } catch (_e) {}
    })();

    // Inject responsive header CSS once
    (function injectHeaderCSS() {
        if (document.getElementById("il-header-responsive-css")) return;
        var style = document.createElement("style");
        style.id = "il-header-responsive-css";
        style.textContent = [
            ".header .main-header{display:flex;align-items:center;justify-content:space-between;flex-wrap:nowrap;gap:14px;position:relative;}",
            ".header .main-header .header-left{display:flex;align-items:center;flex:0 0 auto;min-width:0;}",
            ".header .nav-main-menu{width:auto !important;}",
            "#header-right{display:flex !important;align-items:center;gap:12px;margin-left:auto;flex-shrink:0;}",
            "#header-right #header-lang,#header-right #header-auth{display:flex;align-items:center;}",
            "#header-auth a{outline:none;}",

            "@media (min-width:1200px){",
            "  .header .burger-icon{display:none !important;}",
            "}",

            "@media (max-width:1199.98px){",
            "  .header .nav-main-menu{display:none !important;}",
            "  .header .burger-icon{position:absolute !important;top:50% !important;right:16px !important;transform:translateY(-50%) !important;}",
            "  #header-right{margin-right:50px;gap:10px;}",
            "  #header-auth a{width:38px !important;height:38px !important;}",
            "  #header-auth a svg{width:18px !important;height:18px !important;}",
            "  .header .main-header .header-left .header-logo{margin-right:0 !important;}",
            "  #header-auth a.il-login-btn{padding:0 !important;border-radius:50% !important;justify-content:center !important;gap:0 !important;}",
            "  #header-auth a.il-login-btn .il-login-label{display:none !important;}",
            "}",

            "@media (max-width:767.98px){",
            "  .header{padding:18px 0 !important;}",
            "  .header .main-header .header-left .header-logo{width:120px !important;}",
            "  .header .main-header .header-left .header-logo img{max-width:100%;height:auto;}",
            "  #header-right{margin-right:46px;gap:8px;}",
            "  #header-auth a{width:36px !important;height:36px !important;}",
            "  #site-lang-toggle{padding:2px !important;}",
            "  #site-lang-toggle button{padding:5px 9px !important;font-size:11px !important;}",
            "}",

            "@media (max-width:480px){",
            "  .header .main-header .header-left .header-logo{width:105px !important;}",
            "  #header-right{gap:6px;margin-right:42px;}",
            "  #header-auth a{width:34px !important;height:34px !important;}",
            "  #site-lang-toggle button{padding:4px 7px !important;font-size:10px !important;letter-spacing:0.02em !important;}",
            "}",

            "@media (max-width:359.98px){",
            "  .header .main-header .header-left .header-logo{width:90px !important;}",
            "  #header-right{margin-right:38px;gap:5px;}",
            "  #header-auth a{width:32px !important;height:32px !important;}",
            "  #header-auth a svg{width:16px !important;height:16px !important;}",
            "}"
        ].join("");
        (document.head || document.documentElement).appendChild(style);
    })();

    // Defensive header normalizer.
    //   - Guarantees that every page using `.header > .container > .main-header`
    //     ends up with `<div id="header-right"><div id="header-lang"></div>
    //     <div id="header-auth"></div></div>` as the last child of the main
    //     header bar. This way Login/Profile + language toggle show up in the
    //     top-right of EVERY page, regardless of whether the source HTML
    //     remembers to include the slot.
    function ensureHeaderSlots() {
        var bars = document.querySelectorAll(".header .main-header");
        for (var i = 0; i < bars.length; i += 1) {
            var bar = bars[i];
            var right = bar.querySelector("#header-right");
            if (!right) {
                right = document.createElement("div");
                right.id = "header-right";
                bar.appendChild(right);
            }
            if (!right.querySelector("#header-lang")) {
                var lang = document.createElement("div");
                lang.id = "header-lang";
                right.appendChild(lang);
            }
            if (!right.querySelector("#header-auth")) {
                var auth = document.createElement("div");
                auth.id = "header-auth";
                right.appendChild(auth);
            }
        }
    }

    // Run once as soon as the script body executes (before DOMContentLoaded
    // when the script is at the bottom of <body>) so the right-corner slot
    // appears on first paint with no layout thrash.
    ensureHeaderSlots();

    var API_BASE = "/api";

    var STORAGE_KEYS = {
        access: "interlabour_access_token",
        refresh: "interlabour_refresh_token",
        user: "interlabour_user",
        pendingEmail: "interlabour_pending_email",
        resetEmail: "interlabour_reset_email"
    };

    function getStoredUser() {
        try {
            var raw = localStorage.getItem(STORAGE_KEYS.user);
            return raw ? JSON.parse(raw) : null;
        } catch (err) {
            return null;
        }
    }

    function getAccessToken() {
        try { return localStorage.getItem(STORAGE_KEYS.access) || ""; } catch (_e) { return ""; }
    }

    function getRefreshToken() {
        try { return localStorage.getItem(STORAGE_KEYS.refresh) || ""; } catch (_e) { return ""; }
    }

    // Update only the keys present on the response. After login we get
    // { access, refresh, user }; after a token refresh we get { access, refresh? }
    // and we must NOT wipe the cached user on a refresh round-trip.
    function setSession(data) {
        if (!data) return;
        if (typeof data.access === "string" && data.access) {
            localStorage.setItem(STORAGE_KEYS.access, data.access);
        }
        if (typeof data.refresh === "string" && data.refresh) {
            localStorage.setItem(STORAGE_KEYS.refresh, data.refresh);
        }
        if (data.user && typeof data.user === "object") {
            localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(data.user));
        }
        scheduleProactiveRefresh();
    }

    function clearSession() {
        localStorage.removeItem(STORAGE_KEYS.access);
        localStorage.removeItem(STORAGE_KEYS.refresh);
        localStorage.removeItem(STORAGE_KEYS.user);
        if (_refreshTimer) {
            clearTimeout(_refreshTimer);
            _refreshTimer = null;
        }
    }

    // ---- JWT helpers (decode payload for `exp`; no signature verification) ----
    function parseJwtPayload(token) {
        if (!token || typeof token !== "string") return null;
        var parts = token.split(".");
        if (parts.length !== 3) return null;
        try {
            var b64 = parts[1].replace(/-/g, "+").replace(/_/g, "/");
            var pad = b64.length % 4;
            if (pad) b64 += "=".repeat(4 - pad);
            var raw = atob(b64);
            // utf-8 decode
            var json = decodeURIComponent(
                raw.split("").map(function (c) {
                    return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
                }).join("")
            );
            return JSON.parse(json);
        } catch (_e) {
            return null;
        }
    }

    function getTokenExpiryMs(token) {
        var p = parseJwtPayload(token);
        return p && typeof p.exp === "number" ? p.exp * 1000 : 0;
    }

    function isTokenExpiringSoon(token, marginSec) {
        var expMs = getTokenExpiryMs(token);
        if (!expMs) return true; // unparseable -> treat as expired
        var margin = (typeof marginSec === "number" ? marginSec : 30) * 1000;
        return Date.now() >= expMs - margin;
    }

    // ---- Single-flight refresh + proactive scheduler ----
    var _refreshPromise = null;
    var _refreshTimer = null;

    function refreshAccessToken() {
        if (_refreshPromise) return _refreshPromise;
        var refresh = getRefreshToken();
        if (!refresh) {
            return Promise.reject(new Error("No refresh token available."));
        }

        _refreshPromise = (async function () {
            try {
                var resp = await fetch(API_BASE + "/auth/refresh/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json", "Accept": "application/json" },
                    body: JSON.stringify({ refresh: refresh }),
                    credentials: "same-origin"
                });
                var data = {};
                try { data = await resp.json(); } catch (_e) { data = {}; }
                if (!resp.ok || !data.access) {
                    var msg = (data && (data.detail || data.message)) || "Session expired. Please sign in again.";
                    var err = new Error(msg);
                    err.status = resp.status;
                    throw err;
                }
                setSession({ access: data.access, refresh: data.refresh });
                return data.access;
            } finally {
                _refreshPromise = null;
            }
        })();
        return _refreshPromise;
    }

    function scheduleProactiveRefresh() {
        if (_refreshTimer) {
            clearTimeout(_refreshTimer);
            _refreshTimer = null;
        }
        var access = getAccessToken();
        if (!access) return;
        var expMs = getTokenExpiryMs(access);
        if (!expMs) return;
        // Refresh 60s before expiry; never wait more than ~23h.
        var delay = expMs - Date.now() - 60 * 1000;
        if (delay < 1000) delay = 1000;
        if (delay > 23 * 60 * 60 * 1000) delay = 23 * 60 * 60 * 1000;
        _refreshTimer = setTimeout(function () {
            refreshAccessToken().catch(function () {
                // swallow; the next authed request will surface it
            });
        }, delay);
    }

    async function getValidAccessToken(marginSec) {
        var token = getAccessToken();
        var refresh = getRefreshToken();
        if (token && !isTokenExpiringSoon(token, marginSec)) {
            return token;
        }
        if (!refresh) return "";
        try {
            return await refreshAccessToken();
        } catch (_e) {
            return "";
        }
    }

    function redirectToLogin() {
        var p = window.location.pathname || "";
        var skip = ["login", "register", "forgot-password", "reset-password", "verify-otp"];
        for (var i = 0; i < skip.length; i += 1) {
            if (p.indexOf(skip[i]) !== -1) return;
        }
        var next = encodeURIComponent(p + (window.location.search || ""));
        window.location.href = "/login.html?next=" + next;
    }

    function isAdminRole(user) {
        if (!user) return false;
        if (user.user_type === "admin") return true;
        if (user.is_staff === true) return true;
        if (user.is_superuser === true) return true;
        return false;
    }

    function getDashboardPath(user) {
        if (!user) return "/index.html";
        if (isAdminRole(user)) return "/adminpanel/";
        return "/account/";
    }

    function getAccountPath(user) {
        return isAdminRole(user) ? "/adminpanel/" : "/account/";
    }

    function getMessageFromErrorPayload(payload) {
        if (!payload) return "Something went wrong. Please try again.";
        if (typeof payload === "string") return payload;
        if (payload.detail) return payload.detail;
        if (payload.message) return payload.message;
        var firstKey = Object.keys(payload)[0];
        if (!firstKey) return "Something went wrong. Please try again.";
        var value = payload[firstKey];
        if (Array.isArray(value)) return String(value[0]);
        if (typeof value === "object" && value !== null) {
            var nestedKey = Object.keys(value)[0];
            return nestedKey ? String(value[nestedKey]) : "Something went wrong. Please try again.";
        }
        return String(value);
    }

    // Centralized fetch helper with:
    //  - JSON request/response handling
    //  - Optional Authorization header (auth: true)
    //  - Proactive access-token refresh (when about to expire)
    //  - Single-flight refresh + transparent retry on 401
    //  - Hard-fail to /login.html when refresh itself fails
    //
    // Options:
    //   method, headers, body                  - standard fetch-ish
    //   auth: bool                             - attach Bearer access token
    //   redirectOnAuthFail: bool (default true) - redirect to login on 401 + refresh failure
    //   skipAuthRefresh: bool (default false)  - do not try to refresh before sending
    async function apiFetch(path, options) {
        var requestOptions = options || {};
        var headers = Object.assign(
            { "Content-Type": "application/json", "Accept": "application/json" },
            requestOptions.headers || {}
        );

        if (requestOptions.auth) {
            var token = requestOptions.skipAuthRefresh
                ? getAccessToken()
                : await getValidAccessToken();
            if (token) {
                headers.Authorization = "Bearer " + token;
            }
        }

        var fetchInit = {
            method: requestOptions.method || "GET",
            headers: headers,
            credentials: requestOptions.credentials || "same-origin",
            body: undefined
        };
        if (requestOptions.body !== undefined && requestOptions.body !== null) {
            fetchInit.body = typeof requestOptions.body === "string"
                ? requestOptions.body
                : JSON.stringify(requestOptions.body);
        }

        var response = await fetch(path, fetchInit);

        // Auto-refresh + retry once on 401 for authed requests.
        if (
            response.status === 401 &&
            requestOptions.auth &&
            !requestOptions._retried &&
            getRefreshToken()
        ) {
            try {
                var newToken = await refreshAccessToken();
                if (newToken) {
                    headers.Authorization = "Bearer " + newToken;
                    fetchInit.headers = headers;
                    response = await fetch(path, fetchInit);
                    requestOptions._retried = true;
                }
            } catch (_refreshErr) {
                clearSession();
                refreshAuthNav();
                if (requestOptions.redirectOnAuthFail !== false) {
                    redirectToLogin();
                }
                var err1 = new Error("Session expired. Please sign in again.");
                err1.status = 401;
                throw err1;
            }
        }

        var data = {};
        try { data = await response.json(); } catch (_e) { data = {}; }

        if (!response.ok) {
            // Final 401 (after retry) - blow the session away.
            if (response.status === 401 && requestOptions.auth) {
                clearSession();
                refreshAuthNav();
                if (requestOptions.redirectOnAuthFail !== false) {
                    redirectToLogin();
                }
            }
            var err = new Error(getMessageFromErrorPayload(data));
            err.status = response.status;
            err.payload = data;
            throw err;
        }

        return data;
    }

    // Backwards-compatible alias.
    var request = apiFetch;

    function createLinkItem(menu, href, label, className, isMobile) {
        var li = document.createElement("li");
        if (isMobile) {
            li.className = "has-children";
        } else {
            li.className = className || "";
        }
        li.setAttribute("data-auth-links", "1");

        var a = document.createElement("a");
        a.href = href;
        a.textContent = label;
        if (className) {
            a.className = className;
        }
        li.appendChild(a);
        menu.appendChild(li);
    }

    function applyMobileAuthNav(menu) {
        if (!menu) return;
        var existing = menu.querySelectorAll("[data-auth-links='1']");
        for (var i = 0; i < existing.length; i += 1) {
            existing[i].remove();
        }
        var user = getStoredUser();
        if (!user) {
            createLinkItem(menu, "/login.html", "Login", "", true);
            createLinkItem(menu, "/register.html", "Register", "", true);
            return;
        }
        createLinkItem(menu, getAccountPath(user), isAdminRole(user) ? "Admin Panel" : "My Account", "", true);
        createLinkItem(menu, "#", "Logout", "js-auth-logout", true);
    }

    function renderDesktopAuth(container) {
        if (!container) return;
        var existing = container.querySelectorAll("[data-auth-el]");
        for (var i = 0; i < existing.length; i += 1) {
            existing[i].remove();
        }

        var user = getStoredUser();

        if (!user) {
            var loginBtn = document.createElement("a");
            loginBtn.href = "/login.html";
            loginBtn.title = "Login";
            loginBtn.setAttribute("data-auth-el", "1");
            loginBtn.className = "il-login-btn";
            loginBtn.style.cssText = [
                "display:inline-flex", "align-items:center", "gap:6px",
                "background:linear-gradient(135deg,#19263f,#2d467a)",
                "color:#fff", "padding:8px 20px", "border-radius:999px",
                "font-size:13px", "font-weight:600", "text-decoration:none",
                "box-shadow:0 4px 14px rgba(25,38,63,0.32)", "white-space:nowrap",
                "transition:opacity 0.2s"
            ].join(";");
            loginBtn.innerHTML = [
                "<svg width='14' height='14' viewBox='0 0 24 24' fill='none'",
                " stroke='currentColor' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'>",
                "<path d='M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2'/>",
                "<circle cx='12' cy='7' r='4'/>",
                "</svg>",
                "<span class='il-login-label'>Login</span>"
            ].join("");
            loginBtn.addEventListener("mouseenter", function () { this.style.opacity = "0.88"; });
            loginBtn.addEventListener("mouseleave", function () { this.style.opacity = "1"; });
            container.appendChild(loginBtn);
            return;
        }

        var profileLink = document.createElement("a");
        var acctHref = getAccountPath(user);
        profileLink.href = acctHref;
        profileLink.title = isAdminRole(user)
            ? (user.email ? user.email + " — Admin Panel" : "Admin Panel")
            : (user.email || "My Account");
        profileLink.setAttribute("data-auth-el", "1");
        profileLink.className = "il-header-auth-brand";
        profileLink.style.cssText = [
            "display:inline-flex", "align-items:center", "justify-content:center",
            "width:42px", "height:42px", "border-radius:50%",
            "background:linear-gradient(135deg,#19263f,#2d467a)",
            "color:#fff", "text-decoration:none",
            "box-shadow:0 4px 14px rgba(25,38,63,0.32)",
            "transition:transform 0.15s,box-shadow 0.15s",
            "flex-shrink:0"
        ].join(";");
        profileLink.innerHTML = [
            "<svg width='20' height='20' viewBox='0 0 24 24' fill='none'",
            " stroke='currentColor' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'>",
            "<path d='M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2'/>",
            "<circle cx='12' cy='7' r='4'/>",
            "</svg>"
        ].join("");
        profileLink.addEventListener("mouseenter", function () {
            this.style.transform = "scale(1.06)";
            this.style.boxShadow = "0 6px 18px rgba(25,38,63,0.42)";
        });
        profileLink.addEventListener("mouseleave", function () {
            this.style.transform = "scale(1)";
            this.style.boxShadow = "0 4px 14px rgba(25,38,63,0.32)";
        });
        container.appendChild(profileLink);
    }

    function refreshAuthNav() {
        var headerAuth = document.getElementById("header-auth");
        var desktopFallbackMenus = null;
        if (headerAuth) {
            renderDesktopAuth(headerAuth);
        } else {
            desktopFallbackMenus = document.querySelectorAll(".main-menu");
            for (var i = 0; i < desktopFallbackMenus.length; i += 1) {
                var existing = desktopFallbackMenus[i].querySelectorAll("[data-auth-links='1']");
                for (var k = 0; k < existing.length; k += 1) { existing[k].remove(); }
                var user = getStoredUser();
                if (!user) {
                    createLinkItem(desktopFallbackMenus[i], "/login.html", "Login", "", false);
                    createLinkItem(desktopFallbackMenus[i], "/register.html", "Register", "", false);
                } else {
                    createLinkItem(desktopFallbackMenus[i], getAccountPath(user), isAdminRole(user) ? "Admin Panel" : "My Account", "", false);
                    createLinkItem(desktopFallbackMenus[i], "#", "Logout", "js-auth-logout", false);
                }
            }
        }
        var mobileMenus = document.querySelectorAll(".mobile-menu");
        for (var j = 0; j < mobileMenus.length; j += 1) {
            applyMobileAuthNav(mobileMenus[j]);
        }

        // Re-apply translations to every subtree we just touched. This makes
        // navbar localisation deterministic regardless of whether i18n.js
        // has loaded before this call (it auto-loads async). When SiteI18n
        // isn't ready yet, its own init() will translate the whole body
        // shortly after - so this is purely an optimisation.
        try {
            if (window.SiteI18n && typeof window.SiteI18n.apply === "function") {
                if (headerAuth) window.SiteI18n.apply(headerAuth);
                if (desktopFallbackMenus) {
                    for (var dm = 0; dm < desktopFallbackMenus.length; dm += 1) {
                        window.SiteI18n.apply(desktopFallbackMenus[dm]);
                    }
                }
                for (var m = 0; m < mobileMenus.length; m += 1) {
                    window.SiteI18n.apply(mobileMenus[m]);
                }
            }
        } catch (_e) {}
    }

    async function logoutUser() {
        var refresh = getRefreshToken();
        try {
            await apiFetch(API_BASE + "/auth/logout/", {
                method: "POST",
                auth: true,
                body: { refresh: refresh || "" },
                redirectOnAuthFail: false
            });
        } catch (_err) {
            // Backend may already consider the token invalid - clear locally regardless.
        }
        clearSession();
        refreshAuthNav();
        window.location.href = "/login.html";
    }

    function bindLogoutEvents() {
        document.addEventListener("click", function (event) {
            var target = event.target;
            if (!(target instanceof Element)) return;
            if (target.classList.contains("js-auth-logout")) {
                event.preventDefault();
                logoutUser();
            }
        });
    }

    // Translate a string through the global i18n helper if it is loaded.
    // Falls back to the original text when the helper isn't ready yet
    // (e.g. very first render before i18n.js has initialised).
    function tr(text) {
        try {
            if (window.SiteI18n && typeof window.SiteI18n.translate === "function") {
                return window.SiteI18n.translate(text);
            }
        } catch (_e) {}
        return text;
    }

    function setMessage(element, message, type) {
        if (!element) return;
        element.textContent = tr(message);
        element.style.color = type === "error" ? "#e11d48" : "#0f766e";
    }

    function setButtonLoading(button, isLoading, loadingText, defaultText) {
        if (!button) return;
        button.disabled = isLoading;
        button.textContent = tr(isLoading ? loadingText : defaultText);
    }

    function bindRegisterForm() {
        var form = document.getElementById("register-form");
        if (!form) return;

        var msg = document.getElementById("register-message");
        var button = form.querySelector("button[type='submit']");
        var userTypeSelect = document.getElementById("user_type");

        form.addEventListener("submit", async function (event) {
            event.preventDefault();
            setMessage(msg, "", "success");

            var firstName = document.getElementById("first_name").value.trim();
            var lastName = document.getElementById("last_name").value.trim();
            var email = document.getElementById("email").value.trim().toLowerCase();
            var password = document.getElementById("password").value;
            var confirmPassword = document.getElementById("confirm_password").value;
            var userType = (userTypeSelect && userTypeSelect.value) ? userTypeSelect.value : "normal";

            if (!email || !password) {
                setMessage(msg, "Email and password are required.", "error");
                return;
            }
            if (password !== confirmPassword) {
                setMessage(msg, "Passwords do not match.", "error");
                return;
            }

            var payload = {
                first_name: firstName,
                last_name: lastName,
                email: email,
                password: password,
                user_type: userType
            };

            setButtonLoading(button, true, "Creating account...", "Create Account");
            try {
                await request(API_BASE + "/auth/register/", {
                    method: "POST",
                    body: payload
                });
                localStorage.setItem(STORAGE_KEYS.pendingEmail, email);
                setMessage(msg, "Registration successful. OTP sent to your email.", "success");
                setTimeout(function () {
                    window.location.href = "/verify-otp.html?email=" + encodeURIComponent(email);
                }, 900);
            } catch (err) {
                setMessage(msg, err.message, "error");
            } finally {
                setButtonLoading(button, false, "Creating account...", "Create Account");
            }
        });
    }

    function bindVerifyOtpForm() {
        var form = document.getElementById("verify-otp-form");
        if (!form) return;

        var msg = document.getElementById("verify-message");
        var button = form.querySelector("button[type='submit']");
        var resendBtn = document.getElementById("resend-otp-btn");
        var emailInput = document.getElementById("email");
        var params = new URLSearchParams(window.location.search);
        var emailFromParams = params.get("email");
        var savedEmail = localStorage.getItem(STORAGE_KEYS.pendingEmail);
        if (emailInput) {
            emailInput.value = emailFromParams || savedEmail || "";
        }

        form.addEventListener("submit", async function (event) {
            event.preventDefault();
            setMessage(msg, "", "success");

            var email = emailInput.value.trim().toLowerCase();
            var otp = document.getElementById("otp").value.trim();
            if (!email || !otp) {
                setMessage(msg, "Email and OTP are required.", "error");
                return;
            }

            setButtonLoading(button, true, "Verifying...", "Verify OTP");
            try {
                await request(API_BASE + "/auth/verify-email-otp/", {
                    method: "POST",
                    body: {
                        email: email,
                        otp: otp
                    }
                });
                setMessage(msg, "Email verified successfully. Redirecting to login...", "success");
                localStorage.removeItem(STORAGE_KEYS.pendingEmail);
                setTimeout(function () {
                    window.location.href = "/login.html?email=" + encodeURIComponent(email);
                }, 900);
            } catch (err) {
                setMessage(msg, err.message, "error");
            } finally {
                setButtonLoading(button, false, "Verifying...", "Verify OTP");
            }
        });

        if (resendBtn) {
            resendBtn.addEventListener("click", async function () {
                var email = emailInput.value.trim().toLowerCase();
                if (!email) {
                    setMessage(msg, "Enter your email first.", "error");
                    return;
                }
                setButtonLoading(resendBtn, true, "Sending...", "Resend OTP");
                try {
                    await request(API_BASE + "/auth/resend-email-otp/", {
                        method: "POST",
                        body: { email: email }
                    });
                    setMessage(msg, "OTP sent again. Please check your email.", "success");
                } catch (err) {
                    setMessage(msg, err.message, "error");
                } finally {
                    setButtonLoading(resendBtn, false, "Sending...", "Resend OTP");
                }
            });
        }
    }

    function bindLoginForm() {
        var form = document.getElementById("login-form");
        if (!form) return;

        var msg = document.getElementById("login-message");
        var button = form.querySelector("button[type='submit']");
        var emailInput = document.getElementById("email");
        var params = new URLSearchParams(window.location.search);
        var emailFromParams = params.get("email");
        if (emailInput && emailFromParams) {
            emailInput.value = emailFromParams;
        }

        form.addEventListener("submit", async function (event) {
            event.preventDefault();
            setMessage(msg, "", "success");

            var email = document.getElementById("email").value.trim().toLowerCase();
            var password = document.getElementById("password").value;
            if (!email || !password) {
                setMessage(msg, "Please provide email and password.", "error");
                return;
            }

            setButtonLoading(button, true, "Signing in...", "Sign In");
            try {
                var data = await request(API_BASE + "/auth/login/", {
                    method: "POST",
                    body: {
                        email: email,
                        password: password
                    }
                });
                setSession(data);
                refreshAuthNav();
                setMessage(msg, "Login successful. Redirecting...", "success");
                setTimeout(function () {
                    var user = getStoredUser();
                    var nextUrl = params.get("next");
                    if (nextUrl) {
                        try {
                            var decoded = decodeURIComponent(nextUrl);
                            // Allow only same-origin redirects for safety.
                            if (decoded.indexOf("/") === 0 && decoded.indexOf("//") !== 0) {
                                window.location.href = decoded;
                                return;
                            }
                        } catch (_e) {}
                    }
                    window.location.href = getDashboardPath(user);
                }, 600);
            } catch (err) {
                setMessage(msg, err.message, "error");
            } finally {
                setButtonLoading(button, false, "Signing in...", "Sign In");
            }
        });
    }

    function bindForgotPasswordForm() {
        var form = document.getElementById("forgot-password-form");
        if (!form) return;

        var msg = document.getElementById("forgot-message");
        var button = form.querySelector("button[type='submit']");

        form.addEventListener("submit", async function (event) {
            event.preventDefault();
            setMessage(msg, "", "success");

            var email = document.getElementById("email").value.trim().toLowerCase();
            if (!email) {
                setMessage(msg, "Please enter your email address.", "error");
                return;
            }

            setButtonLoading(button, true, "Sending...", "Send Reset Code");
            try {
                await request(API_BASE + "/auth/forgot-password/", {
                    method: "POST",
                    body: { email: email }
                });
                localStorage.setItem(STORAGE_KEYS.resetEmail, email);
                setMessage(msg, "Reset code sent. Redirecting...", "success");
                setTimeout(function () {
                    window.location.href = "/reset-password.html?email=" + encodeURIComponent(email);
                }, 900);
            } catch (err) {
                setMessage(msg, err.message, "error");
            } finally {
                setButtonLoading(button, false, "Sending...", "Send Reset Code");
            }
        });
    }

    function bindResetPasswordForm() {
        var form = document.getElementById("reset-password-form");
        if (!form) return;

        var msg = document.getElementById("reset-message");
        var button = form.querySelector("button[type='submit']");
        var resendBtn = document.getElementById("resend-reset-btn");
        var emailInput = document.getElementById("email");
        var otpInput = document.getElementById("otp");
        var newPasswordInput = document.getElementById("new_password");
        var confirmPasswordInput = document.getElementById("confirm_password");

        var params = new URLSearchParams(window.location.search);
        var emailFromParams = params.get("email");
        var savedEmail = localStorage.getItem(STORAGE_KEYS.resetEmail);
        if (emailInput) {
            emailInput.value = (emailFromParams || savedEmail || "").trim();
        }

        form.addEventListener("submit", async function (event) {
            event.preventDefault();
            setMessage(msg, "", "success");

            var email = (emailInput.value || "").trim().toLowerCase();
            var otp = (otpInput.value || "").trim();
            var newPassword = newPasswordInput.value;
            var confirmPassword = confirmPasswordInput.value;

            if (!email) {
                setMessage(msg, "Email is required.", "error");
                return;
            }
            if (!otp || otp.length !== 6) {
                setMessage(msg, "Enter the 6-digit code from your email.", "error");
                return;
            }
            if (!newPassword || newPassword.length < 8) {
                setMessage(msg, "Password must be at least 8 characters.", "error");
                return;
            }
            if (newPassword !== confirmPassword) {
                setMessage(msg, "Passwords do not match.", "error");
                return;
            }

            setButtonLoading(button, true, "Updating...", "Update Password");
            try {
                await request(API_BASE + "/auth/reset-password/", {
                    method: "POST",
                    body: {
                        email: email,
                        otp: otp,
                        new_password: newPassword,
                        confirm_password: confirmPassword
                    }
                });
                localStorage.removeItem(STORAGE_KEYS.resetEmail);
                setMessage(
                    msg,
                    "Password updated successfully. Redirecting to login...",
                    "success"
                );
                setTimeout(function () {
                    window.location.href = "/login.html?email=" + encodeURIComponent(email);
                }, 1100);
            } catch (err) {
                setMessage(msg, err.message, "error");
            } finally {
                setButtonLoading(button, false, "Updating...", "Update Password");
            }
        });

        if (resendBtn) {
            resendBtn.addEventListener("click", async function () {
                var email = (emailInput.value || "").trim().toLowerCase();
                if (!email) {
                    setMessage(msg, "Enter your email first.", "error");
                    return;
                }
                setButtonLoading(resendBtn, true, "Sending...", "Resend Code");
                try {
                    await request(API_BASE + "/auth/forgot-password/", {
                        method: "POST",
                        body: { email: email }
                    });
                    setMessage(msg, "A new reset code has been sent.", "success");
                } catch (err) {
                    setMessage(msg, err.message, "error");
                } finally {
                    setButtonLoading(resendBtn, false, "Sending...", "Resend Code");
                }
            });
        }
    }

    window.InterLabourAuth = {
        // HTTP helpers
        apiFetch: apiFetch,
        request: request,
        // Token helpers
        getAccessToken: getAccessToken,
        getRefreshToken: getRefreshToken,
        getValidAccessToken: getValidAccessToken,
        refreshAccessToken: refreshAccessToken,
        isAuthenticated: function () { return !!getRefreshToken(); },
        // Session helpers
        getUser: getStoredUser,
        setSession: setSession,
        clearSession: clearSession,
        logout: logoutUser,
        refreshAuthNav: refreshAuthNav
    };

    function clearSessionIfLogoutFlag() {
        // When Django's admin logout redirects to /?logout=1 it means the
        // server session was destroyed. Clear the local JWT tokens too so the
        // frontend nav switches back to Login / Register immediately.
        var params = new URLSearchParams(window.location.search);
        if (params.get("logout") === "1") {
            clearSession();
            // Remove the flag from the URL without a page reload
            params.delete("logout");
            var newUrl = window.location.pathname + (params.toString() ? "?" + params.toString() : "");
            try { window.history.replaceState({}, "", newUrl); } catch (_e) {}
        }
    }

    // If the access token is missing/expired but we still have a refresh token,
    // exchange it for a fresh access token in the background so that the very
    // first authed request on this page doesn't pay the latency of a 401+retry.
    function bootstrapSession() {
        var access = getAccessToken();
        var refresh = getRefreshToken();
        if (!refresh) return;
        if (!access || isTokenExpiringSoon(access, 30)) {
            refreshAccessToken()
                .then(function () { refreshAuthNav(); })
                .catch(function () {
                    clearSession();
                    refreshAuthNav();
                });
        } else {
            scheduleProactiveRefresh();
        }
    }

    // -----------------------------------------------------------------
    // Mobile off-canvas menu UX hardening
    // -----------------------------------------------------------------
    //
    // The theme (main.js) already wires the burger to toggle
    // body.mobile-menu-active and .mobile-header-active.sidebar-visible.
    // We piggy-back on those state classes to:
    //   - lock body scroll while the menu is open (and restore scroll
    //     position on close - critical on iOS Safari)
    //   - close the menu when the user taps Escape
    //   - inject a discoverable close (x) button into pages whose source
    //     HTML doesn't include one.
    // No jQuery dependency: we use plain DOM APIs and a MutationObserver.
    var _menuOpenScrollY = 0;

    function closeMobileMenu() {
        var container = document.querySelector(".mobile-header-active");
        var burger = document.querySelector(".burger-icon");
        if (container) container.classList.remove("sidebar-visible");
        if (burger) burger.classList.remove("burger-close");
        document.body.classList.remove("mobile-menu-active");
    }

    function lockBodyScroll() {
        if (document.body.classList.contains("il-menu-open")) return;
        _menuOpenScrollY = window.scrollY || window.pageYOffset || 0;
        document.body.style.top = "-" + _menuOpenScrollY + "px";
        document.body.style.position = "fixed";
        document.body.style.width = "100%";
        document.body.classList.add("il-menu-open");
    }

    function unlockBodyScroll() {
        if (!document.body.classList.contains("il-menu-open")) return;
        document.body.classList.remove("il-menu-open");
        document.body.style.position = "";
        document.body.style.top = "";
        document.body.style.width = "";
        window.scrollTo(0, _menuOpenScrollY || 0);
    }

    function injectMobileMenuClose() {
        var wrappers = document.querySelectorAll(".mobile-header-wrapper-style .mobile-header-wrapper-inner");
        for (var i = 0; i < wrappers.length; i += 1) {
            var inner = wrappers[i];
            if (inner.querySelector(".il-mobile-menu-close")) continue;
            var btn = document.createElement("button");
            btn.type = "button";
            btn.className = "il-mobile-menu-close mobile-menu-close";
            btn.setAttribute("aria-label", "Close menu");
            btn.setAttribute("data-i18n-skip", "1");
            btn.innerHTML = "&times;";
            btn.addEventListener("click", function (e) {
                e.preventDefault();
                e.stopPropagation();
                closeMobileMenu();
            });
            // Make the wrapper-inner a positioning context so the absolute
            // close button anchors to the panel.
            if (getComputedStyle(inner).position === "static") {
                inner.style.position = "relative";
            }
            inner.appendChild(btn);
        }
    }

    function watchMobileMenuState() {
        if (!("MutationObserver" in window)) return;
        var observer = new MutationObserver(function () {
            if (document.body.classList.contains("mobile-menu-active")) {
                lockBodyScroll();
            } else {
                unlockBodyScroll();
            }
        });
        observer.observe(document.body, { attributes: true, attributeFilter: ["class"] });
    }

    function bindMobileMenuKeys() {
        document.addEventListener("keydown", function (e) {
            if ((e.key === "Escape" || e.key === "Esc") &&
                document.body.classList.contains("mobile-menu-active")) {
                closeMobileMenu();
            }
        });
    }

    function setupMobileMenuUX() {
        injectMobileMenuClose();
        watchMobileMenuState();
        bindMobileMenuKeys();
        // If the page loads while the menu is somehow open (rare), make
        // sure the lock state is consistent.
        if (document.body.classList.contains("mobile-menu-active")) {
            lockBodyScroll();
        }
    }

    // -----------------------------------------------------------------
    // Image performance: lazy-load + async decode for every <img> that
    // isn't critical above-the-fold (header logo, hero banner). This is
    // additive and entirely non-destructive: we never touch images that
    // already declare `loading` or `decoding`, so explicit page-level
    // overrides remain authoritative.
    // -----------------------------------------------------------------
    function isCriticalImage(img) {
        // Walk up to a small depth and bail if the image lives inside
        // the header or the hero banner: those need to render asap.
        var node = img;
        var depth = 0;
        while (node && depth < 8) {
            if (node.classList && (
                node.classList.contains("header") ||
                node.classList.contains("banner-hero") ||
                node.classList.contains("banner-home-3") ||
                node.classList.contains("header-logo") ||
                node.classList.contains("mobile-header-active")
            )) {
                return true;
            }
            node = node.parentNode;
            depth += 1;
        }
        return false;
    }

    function optimiseImages(root) {
        var scope = root || document;
        if (!scope.querySelectorAll) return;
        var imgs = scope.querySelectorAll("img");
        for (var i = 0; i < imgs.length; i += 1) {
            var img = imgs[i];
            if (!img || img.tagName !== "IMG") continue;
            if (!img.hasAttribute("decoding")) {
                img.setAttribute("decoding", "async");
            }
            if (!img.hasAttribute("loading") && !isCriticalImage(img)) {
                img.setAttribute("loading", "lazy");
            }
        }
    }

    // Re-run when dynamic loaders inject new content (jobs / services /
    // blog list etc.). They don't notify us, so we observe the body for
    // added <img> nodes and patch them in place.
    function watchDynamicImages() {
        if (!("MutationObserver" in window)) return;
        var observer = new MutationObserver(function (mutations) {
            for (var i = 0; i < mutations.length; i += 1) {
                var added = mutations[i].addedNodes || [];
                for (var j = 0; j < added.length; j += 1) {
                    var node = added[j];
                    if (node && node.nodeType === 1) {
                        if (node.tagName === "IMG") {
                            if (!node.hasAttribute("decoding")) node.setAttribute("decoding", "async");
                            if (!node.hasAttribute("loading") && !isCriticalImage(node)) {
                                node.setAttribute("loading", "lazy");
                            }
                        } else if (node.querySelectorAll) {
                            optimiseImages(node);
                        }
                    }
                }
            }
        });
        observer.observe(document.body, { childList: true, subtree: true });
    }

    // Newsletter forms exist across many static pages. Point them at the backend
    // subscribe endpoint so a confirmation email is sent.
    function wireNewsletterForms() {
        var forms = document.querySelectorAll("form.form-newsletter");
        for (var i = 0; i < forms.length; i += 1) {
            var form = forms[i];
            try {
                if (form.getAttribute("data-il-wired") === "1") continue;
                form.setAttribute("data-il-wired", "1");

                form.method = "post";
                form.action = "/jobs/alerts/subscribe/";

                var input =
                    form.querySelector('input[name="email"]') ||
                    form.querySelector('input[type="email"]') ||
                    form.querySelector("input");
                if (input) {
                    input.setAttribute("name", "email");
                    input.setAttribute("type", "email");
                    input.setAttribute("required", "required");
                    input.setAttribute("autocomplete", "email");
                }

                var next = form.querySelector('input[name="next"]');
                if (!next) {
                    next = document.createElement("input");
                    next.type = "hidden";
                    next.name = "next";
                    form.appendChild(next);
                }
                next.value = window.location.pathname || "/jobs/";
            } catch (_e) {}
        }
    }

    document.addEventListener("DOMContentLoaded", function () {
        clearSessionIfLogoutFlag();
        ensureHeaderSlots();
        refreshAuthNav();
        bootstrapSession();
        bindLogoutEvents();
        bindRegisterForm();
        bindVerifyOtpForm();
        bindLoginForm();
        bindForgotPasswordForm();
        bindResetPasswordForm();
        setupMobileMenuUX();
        wireNewsletterForms();
        optimiseImages(document);
        watchDynamicImages();
    });

    // When the tab becomes visible again after being hidden for a while, the
    // access token may have expired - top it up before any user interaction.
    document.addEventListener("visibilitychange", function () {
        if (document.visibilityState === "visible") {
            var refresh = getRefreshToken();
            if (!refresh) return;
            var access = getAccessToken();
            if (!access || isTokenExpiringSoon(access, 60)) {
                refreshAccessToken().catch(function () {
                    clearSession();
                    refreshAuthNav();
                });
            }
        }
    });
})();
