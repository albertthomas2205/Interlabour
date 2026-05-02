/* Inter Labour - Dynamic home content
 *
 * 1. Replaces the static "What Our Clients Say" testimonial cards with live
 *    testimonials from /api/testimonials/.
 * 2. Replaces the static partner-logos strip with a smooth, infinite,
 *    auto-scrolling marquee fed from /api/partners/.
 *
 * Runs on the home page only.
 */
(function () {
    "use strict";

    function escapeHtml(value) {
        return String(value == null ? "" : value)
            .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
    }

    function isHomePage() {
        var p = window.location.pathname;
        return p === "/" || p === "/index.html" || p === "/index";
    }

    /* ────────────────────────────────────────────────────────────────────── */
    /* TESTIMONIALS                                                          */
    /* ────────────────────────────────────────────────────────────────────── */

    function findTestimonialsSection() {
        // Locate by heading text — "Wat Onze Klanten Zeggen" / "What Our Clients Say"
        var headings = document.querySelectorAll("h2.section-title");
        for (var i = 0; i < headings.length; i += 1) {
            var t = (headings[i].textContent || "").trim().toLowerCase();
            if (t.indexOf("klanten") !== -1 || t.indexOf("clients say") !== -1 || t.indexOf("what our clients") !== -1) {
                var section = headings[i].closest("section.section-box");
                if (section) return section;
            }
        }
        return null;
    }

    function buildStars(rating) {
        var n = Math.max(0, Math.min(5, parseInt(rating || 5, 10)));
        var html = "";
        for (var i = 0; i < 5; i += 1) {
            html += '<span style="color:' + (i < n ? "#f59e0b" : "#e2e8f0") + ';font-size:18px;">★</span>';
        }
        return html;
    }

    function buildTestimonialCard(t) {
        var photo = t.photo_url || "/assets/imgs/page/about/profile.png";
        var role = t.author_role || "";
        var msg = t.message || "";
        return (
            '<div class="swiper-slide">' +
                '<div class="card-grid-3 hover-up" style="background:#fff;border-radius:14px;padding:28px 24px;box-shadow:0 6px 20px rgba(15,23,42,0.06);height:100%;">' +
                    '<div class="text-center" style="margin-bottom:14px;">' +
                        '<img alt="' + escapeHtml(t.author_name) + '" src="' + escapeHtml(photo) +
                        '" style="width:80px;height:80px;border-radius:50%;object-fit:cover;border:3px solid #eef2ff;" />' +
                    '</div>' +
                    '<p class="text-center" style="font-size:0.95rem;color:#475569;line-height:1.6;font-style:italic;margin:0 0 18px;min-height:96px;">' +
                        '“' + escapeHtml(msg) + '”' +
                    '</p>' +
                    '<div class="text-center" style="margin-bottom:12px;">' + buildStars(t.rating) + '</div>' +
                    '<div class="text-center">' +
                        '<strong style="color:#05264e;font-size:1rem;display:block;">' + escapeHtml(t.author_name) + '</strong>' +
                        '<span style="color:#64748b;font-size:0.85rem;">' + escapeHtml(role) + '</span>' +
                    '</div>' +
                '</div>' +
            '</div>'
        );
    }

    async function loadTestimonials() {
        try {
            var resp = await fetch("/api/testimonials/", { headers: { Accept: "application/json" } });
            if (!resp.ok) return [];
            var data = await resp.json();
            return Array.isArray(data) ? data : (data.results || []);
        } catch (_e) {
            return [];
        }
    }

    function renderTestimonials(section, items) {
        var wrapper = section.querySelector(".swiper-wrapper");

        // Always inject the "Leave a review" CTA, even if no testimonials yet
        injectReviewCta(section);

        if (!wrapper) return;
        if (!items.length) {
            // Show empty state but keep the section visible so the CTA still shows
            wrapper.innerHTML = (
                '<div class="swiper-slide" style="width:100%;">' +
                    '<div style="text-align:center;padding:40px 20px;color:#94a3b8;font-size:0.95rem;">' +
                        '<p>' + (currentLang() === "en"
                            ? "Be the first to share your experience!"
                            : "Wees de eerste om je ervaring te delen!") + '</p>' +
                    '</div>' +
                '</div>'
            );
            return;
        }
        var html = "";
        items.forEach(function (t) { html += buildTestimonialCard(t); });
        wrapper.innerHTML = html;

        // Re-init swiper if the theme has it
        try {
            var container = section.querySelector(".swiper-container");
            if (container && window.Swiper) {
                /* eslint-disable no-new */
                new window.Swiper(container, {
                    slidesPerView: 3,
                    spaceBetween: 30,
                    autoplay: { delay: 4000, disableOnInteraction: false },
                    breakpoints: {
                        0: { slidesPerView: 1 },
                        768: { slidesPerView: 2 },
                        1024: { slidesPerView: 3 }
                    }
                });
            }
        } catch (_e) {}

        if (window.SiteI18n && typeof window.SiteI18n.apply === "function") {
            window.SiteI18n.apply(section);
        }
    }

    function currentLang() {
        if (window.SiteI18n && typeof window.SiteI18n.getLang === "function") {
            return window.SiteI18n.getLang();
        }
        return "nl";
    }

    /* ────────────────────────────────────────────────────────────────────── */
    /* "Leave a review" CTA + modal                                           */
    /* ────────────────────────────────────────────────────────────────────── */

    function injectReviewCta(section) {
        if (section.querySelector(".il-review-cta")) return;
        var lang = currentLang();
        var cta = document.createElement("div");
        cta.className = "il-review-cta";
        cta.style.cssText = "text-align:center;margin-top:40px;";
        cta.innerHTML = (
            '<button type="button" id="il-open-review-modal" ' +
            'style="display:inline-flex;align-items:center;gap:8px;' +
            'background:linear-gradient(135deg,#6366f1,#2563eb);color:#fff;' +
            'border:none;padding:12px 28px;border-radius:999px;font-weight:600;' +
            'font-size:0.95rem;cursor:pointer;box-shadow:0 6px 20px rgba(37,99,235,0.32);' +
            'transition:transform .15s,box-shadow .15s;">' +
                '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">' +
                    '<path d="M12 .587l3.668 7.568L24 9.748l-6 5.852L19.336 24 12 19.897 4.664 24 6 15.6 0 9.748l8.332-1.593z"/>' +
                '</svg>' +
                (lang === "en" ? "Leave a Review" : "Schrijf een Review") +
            '</button>'
        );
        section.querySelector(".container").appendChild(cta);

        cta.querySelector("#il-open-review-modal").addEventListener("click", openReviewModal);
        cta.querySelector("#il-open-review-modal").addEventListener("mouseenter", function () {
            this.style.transform = "translateY(-2px)";
            this.style.boxShadow = "0 10px 26px rgba(37,99,235,0.42)";
        });
        cta.querySelector("#il-open-review-modal").addEventListener("mouseleave", function () {
            this.style.transform = "translateY(0)";
            this.style.boxShadow = "0 6px 20px rgba(37,99,235,0.32)";
        });
    }

    function ensureModalStyles() {
        if (document.getElementById("il-review-style")) return;
        var s = document.createElement("style");
        s.id = "il-review-style";
        s.textContent = [
            ".il-modal{position:fixed;inset:0;background:rgba(15,23,42,0.55);z-index:99999;display:flex;align-items:center;justify-content:center;padding:20px;backdrop-filter:blur(4px);animation:il-fade .15s ease;}",
            "@keyframes il-fade{from{opacity:0;}to{opacity:1;}}",
            ".il-modal-card{background:#fff;border-radius:16px;width:100%;max-width:520px;max-height:90vh;overflow:auto;box-shadow:0 20px 50px rgba(0,0,0,0.3);animation:il-pop .2s ease;}",
            "@keyframes il-pop{from{opacity:0;transform:scale(0.95);}to{opacity:1;transform:scale(1);}}",
            ".il-modal-head{display:flex;justify-content:space-between;align-items:center;padding:22px 26px 14px;border-bottom:1px solid #f1f5f9;}",
            ".il-modal-head h3{margin:0;font-size:1.15rem;color:#0f172a;font-weight:700;}",
            ".il-modal-close{background:transparent;border:none;font-size:24px;color:#94a3b8;cursor:pointer;padding:4px 8px;line-height:1;}",
            ".il-modal-close:hover{color:#0f172a;}",
            ".il-modal-body{padding:22px 26px;}",
            ".il-modal-body label{display:block;font-size:13px;font-weight:600;color:#384152;margin-bottom:6px;}",
            ".il-modal-body input,.il-modal-body textarea{width:100%;border:1px solid #e0e6f7;border-radius:8px;padding:10px 14px;font-size:14px;background:#fff;color:#384152;font-family:inherit;}",
            ".il-modal-body input:focus,.il-modal-body textarea:focus{outline:none;border-color:#3c65f5;box-shadow:0 0 0 3px rgba(60,101,245,.12);}",
            ".il-modal-body .form-row{margin-bottom:14px;}",
            ".il-rating-stars{display:inline-flex;gap:4px;font-size:28px;cursor:pointer;}",
            ".il-rating-stars span{color:#e2e8f0;transition:color .1s;}",
            ".il-rating-stars span.active{color:#f59e0b;}",
            ".il-modal-foot{display:flex;justify-content:flex-end;gap:8px;padding:16px 26px 22px;border-top:1px solid #f1f5f9;}",
            ".il-btn{padding:10px 22px;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;border:none;font-family:inherit;}",
            ".il-btn-primary{background:linear-gradient(135deg,#6366f1,#2563eb);color:#fff;}",
            ".il-btn-primary:disabled{opacity:0.6;cursor:wait;}",
            ".il-btn-ghost{background:#f1f5f9;color:#475569;}",
            ".il-msg{padding:10px 14px;border-radius:8px;font-size:13px;margin-bottom:14px;}",
            ".il-msg.success{background:#ecfdf5;color:#14532d;border:1px solid #bbf7d0;}",
            ".il-msg.error{background:#fef2f2;color:#7f1d1d;border:1px solid #fecaca;}"
        ].join("");
        document.head.appendChild(s);
    }

    function getStoredUser() {
        try {
            var raw = localStorage.getItem("interlabour_user");
            return raw ? JSON.parse(raw) : null;
        } catch (_e) {
            return null;
        }
    }

    function getAccessToken() {
        try { return localStorage.getItem("interlabour_access_token") || ""; } catch (_e) { return ""; }
    }

    function openReviewModal() {
        ensureModalStyles();
        var lang = currentLang();
        var user = getStoredUser();

        if (!user) {
            // Encourage login first
            var go = window.confirm(lang === "en"
                ? "Please log in to leave a review. Go to login page?"
                : "Log in om een review achter te laten. Naar inlogpagina?");
            if (go) window.location.href = "/login.html?next=/";
            return;
        }

        if (document.getElementById("il-review-modal")) return;

        var translations = lang === "en" ? {
            title: "Leave a Review",
            name: "Your name",
            role: "Role / Company (optional)",
            rolePh: "e.g. Operations Manager, Acme Corp",
            message: "Your review",
            messagePh: "Tell us about your experience…",
            rating: "Rating",
            cancel: "Cancel",
            submit: "Submit Review",
            submitting: "Submitting…",
            thanks: "Thanks for your review! It will appear once approved by our team.",
            errMsg: "Please write your review.",
            errGeneric: "Could not submit your review. Please try again."
        } : {
            title: "Schrijf een Review",
            name: "Je naam",
            role: "Functie / Bedrijf (optioneel)",
            rolePh: "bijv. Operations Manager, Acme B.V.",
            message: "Je review",
            messagePh: "Vertel ons over je ervaring…",
            rating: "Beoordeling",
            cancel: "Annuleren",
            submit: "Review versturen",
            submitting: "Versturen…",
            thanks: "Bedankt voor je review! Hij verschijnt zodra ons team hem heeft goedgekeurd.",
            errMsg: "Schrijf alsjeblieft een review.",
            errGeneric: "Verzenden mislukt. Probeer het opnieuw."
        };

        var modal = document.createElement("div");
        modal.id = "il-review-modal";
        modal.className = "il-modal";
        modal.innerHTML = (
            '<div class="il-modal-card" role="dialog" aria-modal="true">' +
                '<div class="il-modal-head">' +
                    '<h3>' + escapeHtml(translations.title) + '</h3>' +
                    '<button type="button" class="il-modal-close" aria-label="Close">×</button>' +
                '</div>' +
                '<form id="il-review-form" novalidate>' +
                    '<div class="il-modal-body">' +
                        '<div class="il-msg-slot"></div>' +
                        '<div class="form-row">' +
                            '<label for="il-rev-name">' + escapeHtml(translations.name) + '</label>' +
                            '<input type="text" id="il-rev-name" required value="' +
                                escapeHtml(((user.first_name || "") + " " + (user.last_name || "")).trim() || user.email || "") + '" />' +
                        '</div>' +
                        '<div class="form-row">' +
                            '<label for="il-rev-role">' + escapeHtml(translations.role) + '</label>' +
                            '<input type="text" id="il-rev-role" placeholder="' + escapeHtml(translations.rolePh) + '" />' +
                        '</div>' +
                        '<div class="form-row">' +
                            '<label>' + escapeHtml(translations.rating) + '</label>' +
                            '<div class="il-rating-stars" id="il-rev-rating">' +
                                '<span data-v="1">★</span><span data-v="2">★</span><span data-v="3">★</span>' +
                                '<span data-v="4">★</span><span data-v="5">★</span>' +
                            '</div>' +
                        '</div>' +
                        '<div class="form-row">' +
                            '<label for="il-rev-msg">' + escapeHtml(translations.message) + '</label>' +
                            '<textarea id="il-rev-msg" rows="4" required placeholder="' +
                                escapeHtml(translations.messagePh) + '"></textarea>' +
                        '</div>' +
                    '</div>' +
                    '<div class="il-modal-foot">' +
                        '<button type="button" class="il-btn il-btn-ghost il-modal-close-2">' +
                            escapeHtml(translations.cancel) + '</button>' +
                        '<button type="submit" class="il-btn il-btn-primary">' +
                            escapeHtml(translations.submit) + '</button>' +
                    '</div>' +
                '</form>' +
            '</div>'
        );
        document.body.appendChild(modal);

        function close() { modal.remove(); }
        modal.addEventListener("click", function (e) { if (e.target === modal) close(); });
        modal.querySelector(".il-modal-close").addEventListener("click", close);
        modal.querySelector(".il-modal-close-2").addEventListener("click", close);

        var rating = 5;
        var stars = modal.querySelectorAll("#il-rev-rating span");
        function paintStars(v) {
            stars.forEach(function (st, i) {
                if (i < v) st.classList.add("active");
                else st.classList.remove("active");
            });
        }
        paintStars(rating);
        stars.forEach(function (st) {
            st.addEventListener("mouseenter", function () { paintStars(parseInt(st.dataset.v, 10)); });
            st.addEventListener("click", function () {
                rating = parseInt(st.dataset.v, 10);
                paintStars(rating);
            });
        });
        modal.querySelector("#il-rev-rating").addEventListener("mouseleave", function () { paintStars(rating); });

        var form = modal.querySelector("#il-review-form");
        var submitBtn = form.querySelector("button[type=submit]");
        var msgSlot = form.querySelector(".il-msg-slot");

        function showMsg(text, type) {
            msgSlot.innerHTML = '<div class="il-msg ' + type + '">' + escapeHtml(text) + '</div>';
        }

        form.addEventListener("submit", async function (e) {
            e.preventDefault();
            var name = form.querySelector("#il-rev-name").value.trim();
            var role = form.querySelector("#il-rev-role").value.trim();
            var msg = form.querySelector("#il-rev-msg").value.trim();
            if (!msg) { showMsg(translations.errMsg, "error"); return; }

            submitBtn.disabled = true;
            submitBtn.textContent = translations.submitting;

            var payload = {
                author_name: name,
                rating: rating
            };
            if (lang === "nl") {
                payload.message_nl = msg;
                payload.author_role_nl = role;
            } else {
                payload.message_en = msg;
                payload.author_role_en = role;
            }

            try {
                var headers = { "Content-Type": "application/json", "Accept": "application/json" };
                var token = getAccessToken();
                if (token) headers.Authorization = "Bearer " + token;

                var resp = await fetch("/api/testimonials/", {
                    method: "POST",
                    headers: headers,
                    body: JSON.stringify(payload)
                });
                if (!resp.ok) {
                    var errData = {};
                    try { errData = await resp.json(); } catch (_e) {}
                    var errText = errData.detail || errData.message || translations.errGeneric;
                    if (typeof errData === "object" && !errData.detail) {
                        var firstKey = Object.keys(errData)[0];
                        if (firstKey) {
                            var v = errData[firstKey];
                            errText = Array.isArray(v) ? v[0] : (typeof v === "string" ? v : errText);
                        }
                    }
                    throw new Error(errText);
                }
                showMsg(translations.thanks, "success");
                form.querySelector("#il-rev-msg").value = "";
                setTimeout(close, 2200);
            } catch (err) {
                showMsg(err.message || translations.errGeneric, "error");
                submitBtn.disabled = false;
                submitBtn.textContent = translations.submit;
            }
        });
    }

    /* ────────────────────────────────────────────────────────────────────── */
    /* PARTNERS / CLIENT LOGOS — infinite auto-scroll marquee                 */
    /* ────────────────────────────────────────────────────────────────────── */

    function findPartnerStrip() {
        return document.querySelector("ul.list-partners");
    }

    function ensureMarqueeStyles() {
        if (document.getElementById("il-marquee-style")) return;
        var s = document.createElement("style");
        s.id = "il-marquee-style";
        s.textContent = [
            ".il-marquee{position:relative;overflow:hidden;width:100%;padding:8px 0;mask-image:linear-gradient(to right,transparent,#000 8%,#000 92%,transparent);}",
            ".il-marquee-track{display:flex;gap:60px;align-items:center;width:max-content;animation:il-marquee 35s linear infinite;}",
            ".il-marquee:hover .il-marquee-track{animation-play-state:paused;}",
            ".il-marquee-item{flex:0 0 auto;display:flex;align-items:center;justify-content:center;height:60px;min-width:140px;transition:transform .25s ease,filter .25s ease;filter:grayscale(100%) opacity(0.65);}",
            ".il-marquee-item:hover{transform:translateY(-2px);filter:grayscale(0) opacity(1);}",
            ".il-marquee-item img{max-height:42px;max-width:160px;object-fit:contain;}",
            "@keyframes il-marquee{from{transform:translateX(0);}to{transform:translateX(-50%);}}",
            "@media (max-width:600px){.il-marquee-track{gap:36px;}.il-marquee-item{min-width:110px;height:48px;}.il-marquee-item img{max-height:32px;max-width:120px;}}"
        ].join("");
        (document.head || document.documentElement).appendChild(s);
    }

    function buildPartnerHtml(partners) {
        // Duplicate the list so the CSS keyframe at -50% loops seamlessly
        var doubled = partners.concat(partners);
        return doubled.map(function (p) {
            var src = p.logo_image_url || p.logo_url || "";
            if (!src) return "";
            var name = p.name || "Partner";
            var inner = '<img alt="' + escapeHtml(name) + '" src="' + escapeHtml(src) + '" />';
            if (p.website) {
                return '<div class="il-marquee-item"><a href="' + escapeHtml(p.website) +
                    '" target="_blank" rel="noopener">' + inner + "</a></div>";
            }
            return '<div class="il-marquee-item">' + inner + "</div>";
        }).join("");
    }

    async function loadPartners() {
        try {
            var resp = await fetch("/api/partners/", { headers: { Accept: "application/json" } });
            if (!resp.ok) return [];
            var data = await resp.json();
            return Array.isArray(data) ? data : (data.results || []);
        } catch (_e) {
            return [];
        }
    }

    function renderPartners(strip, partners) {
        if (!strip) return;
        var parent = strip.parentElement;
        if (!partners.length) {
            // Don't show empty strip
            if (parent && parent.parentElement) parent.parentElement.style.display = "none";
            return;
        }
        ensureMarqueeStyles();

        // Replace the legacy <ul> with a marquee div (preserves layout container)
        var marquee = document.createElement("div");
        marquee.className = "il-marquee";
        marquee.setAttribute("aria-label", "Trusted partners");

        var track = document.createElement("div");
        track.className = "il-marquee-track";
        track.innerHTML = buildPartnerHtml(partners);
        marquee.appendChild(track);

        strip.replaceWith(marquee);
    }

    /* ────────────────────────────────────────────────────────────────────── */

    function init() {
        if (!isHomePage()) return;

        var section = findTestimonialsSection();
        if (section) {
            loadTestimonials().then(function (items) { renderTestimonials(section, items); });
        }

        var strip = findPartnerStrip();
        if (strip) {
            loadPartners().then(function (partners) { renderPartners(strip, partners); });
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
