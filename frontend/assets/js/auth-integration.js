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
        inject("/assets/js/dynamic-jobs.js", "data-dyn-jobs-loader");
        inject("/assets/js/dynamic-services.js", "data-dyn-services-loader");
        inject("/assets/js/dynamic-blog.js", "data-dyn-blog-loader");
        inject("/assets/js/dynamic-home.js", "data-dyn-home-loader");
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

    var API_BASE = "/api";

    var STORAGE_KEYS = {
        access: "interlabour_access_token",
        refresh: "interlabour_refresh_token",
        user: "interlabour_user",
        pendingEmail: "interlabour_pending_email"
    };

    function getStoredUser() {
        try {
            var raw = localStorage.getItem(STORAGE_KEYS.user);
            return raw ? JSON.parse(raw) : null;
        } catch (err) {
            return null;
        }
    }

    function setSession(data) {
        localStorage.setItem(STORAGE_KEYS.access, data.access || "");
        localStorage.setItem(STORAGE_KEYS.refresh, data.refresh || "");
        localStorage.setItem(STORAGE_KEYS.user, JSON.stringify(data.user || null));
    }

    function clearSession() {
        localStorage.removeItem(STORAGE_KEYS.access);
        localStorage.removeItem(STORAGE_KEYS.refresh);
        localStorage.removeItem(STORAGE_KEYS.user);
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

    async function request(path, options) {
        var requestOptions = options || {};
        var headers = requestOptions.headers || {};
        headers["Content-Type"] = "application/json";

        if (requestOptions.auth) {
            var accessToken = localStorage.getItem(STORAGE_KEYS.access);
            if (accessToken) {
                headers.Authorization = "Bearer " + accessToken;
            }
        }

        var response = await fetch(path, {
            method: requestOptions.method || "GET",
            headers: headers,
            body: requestOptions.body ? JSON.stringify(requestOptions.body) : undefined
        });

        var data = {};
        try {
            data = await response.json();
        } catch (err) {
            data = {};
        }

        if (!response.ok) {
            throw new Error(getMessageFromErrorPayload(data));
        }

        return data;
    }

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
            loginBtn.setAttribute("data-auth-el", "1");
            loginBtn.style.cssText = [
                "display:inline-flex", "align-items:center", "gap:6px",
                "background:linear-gradient(135deg,#6366f1,#2563eb)",
                "color:#fff", "padding:8px 20px", "border-radius:999px",
                "font-size:13px", "font-weight:600", "text-decoration:none",
                "box-shadow:0 4px 14px rgba(37,99,235,0.32)", "white-space:nowrap",
                "transition:opacity 0.2s"
            ].join(";");
            loginBtn.innerHTML = [
                "<svg width='14' height='14' viewBox='0 0 24 24' fill='none'",
                " stroke='currentColor' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'>",
                "<path d='M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2'/>",
                "<circle cx='12' cy='7' r='4'/>",
                "</svg> Login"
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
        profileLink.style.cssText = [
            "display:inline-flex", "align-items:center", "justify-content:center",
            "width:42px", "height:42px", "border-radius:50%",
            "background:linear-gradient(135deg,#6366f1,#2563eb)",
            "color:#fff", "text-decoration:none",
            "box-shadow:0 4px 14px rgba(37,99,235,0.32)",
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
            this.style.boxShadow = "0 6px 18px rgba(37,99,235,0.42)";
        });
        profileLink.addEventListener("mouseleave", function () {
            this.style.transform = "scale(1)";
            this.style.boxShadow = "0 4px 14px rgba(37,99,235,0.32)";
        });
        container.appendChild(profileLink);
    }

    function refreshAuthNav() {
        var headerAuth = document.getElementById("header-auth");
        if (headerAuth) {
            renderDesktopAuth(headerAuth);
        } else {
            var desktopMenus = document.querySelectorAll(".main-menu");
            for (var i = 0; i < desktopMenus.length; i += 1) {
                var existing = desktopMenus[i].querySelectorAll("[data-auth-links='1']");
                for (var k = 0; k < existing.length; k += 1) { existing[k].remove(); }
                var user = getStoredUser();
                if (!user) {
                    createLinkItem(desktopMenus[i], "/login.html", "Login", "", false);
                    createLinkItem(desktopMenus[i], "/register.html", "Register", "", false);
                } else {
                    createLinkItem(desktopMenus[i], getAccountPath(user), isAdminRole(user) ? "Admin Panel" : "My Account", "", false);
                    createLinkItem(desktopMenus[i], "#", "Logout", "js-auth-logout", false);
                }
            }
        }
        var mobileMenus = document.querySelectorAll(".mobile-menu");
        for (var j = 0; j < mobileMenus.length; j += 1) {
            applyMobileAuthNav(mobileMenus[j]);
        }
    }

    async function logoutUser() {
        var refresh = localStorage.getItem(STORAGE_KEYS.refresh);
        try {
            await request(API_BASE + "/auth/logout/", {
                method: "POST",
                auth: true,
                body: { refresh: refresh || "" }
            });
        } catch (err) {
            // Ignore backend logout errors and clear local session anyway.
        }
        clearSession();
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

    function setMessage(element, message, type) {
        if (!element) return;
        element.textContent = message;
        element.style.color = type === "error" ? "#e11d48" : "#0f766e";
    }

    function setButtonLoading(button, isLoading, loadingText, defaultText) {
        if (!button) return;
        button.disabled = isLoading;
        button.textContent = isLoading ? loadingText : defaultText;
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
                    window.location.href = getDashboardPath(user);
                }, 600);
            } catch (err) {
                setMessage(msg, err.message, "error");
            } finally {
                setButtonLoading(button, false, "Signing in...", "Sign In");
            }
        });
    }

    window.InterLabourAuth = {
        request: request,
        getUser: getStoredUser,
        clearSession: clearSession,
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

    document.addEventListener("DOMContentLoaded", function () {
        clearSessionIfLogoutFlag();
        refreshAuthNav();
        bindLogoutEvents();
        bindRegisterForm();
        bindVerifyOtpForm();
        bindLoginForm();
    });
})();
