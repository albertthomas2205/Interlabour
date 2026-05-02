/* Inter Labour - Dynamic services loader for the Services page
 *
 * Replaces the static service cards with live data from /api/services/
 * Triggers re-translation via window.SiteI18n.apply() after rendering.
 */
(function () {
    "use strict";

    function escapeHtml(value) {
        return String(value == null ? "" : value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function defaultImage() {
        return "/assets/imgs/page/services/recrtmnt.jpg";
    }

    function buildCard(service, index) {
        var name = service.name || "";
        var desc = service.short_description || service.details || "";
        if (desc.length > 220) desc = desc.slice(0, 220) + "…";
        var image = service.image_url || defaultImage();
        var delay = (index % 3) * 0.2;

        return (
            '<div class="col-lg-4 col-md-6 col-sm-6 col-12">' +
                '<div class="card-grid-news hover-up wow animate__animated animate__fadeIn" data-wow-delay="' + delay + 's">' +
                    '<div class="block-image-rd">' +
                        '<figure><img src="' + escapeHtml(image) + '" alt="' + escapeHtml(name) + '" /></figure>' +
                    '</div>' +
                    '<div class="card-info-bottom">' +
                        '<a href="#"><strong>' + escapeHtml(name) + '</strong></a>' +
                        '<p class="text-gray-200">' + escapeHtml(desc) + '</p>' +
                    '</div>' +
                '</div>' +
            '</div>'
        );
    }

    function isServicesPage() {
        var p = window.location.pathname.toLowerCase();
        return p === "/page-service.html" || p === "/page-services.html" || p.endsWith("/services") || p.endsWith("/services/");
    }

    async function loadServices() {
        try {
            var resp = await fetch("/api/services/?page_size=24", { headers: { "Accept": "application/json" } });
            if (!resp.ok) return [];
            var data = await resp.json();
            return Array.isArray(data) ? data : (data.results || []);
        } catch (_e) {
            return [];
        }
    }

    function findContainer() {
        var rows = document.querySelectorAll(".section-box .row.mt-100");
        for (var i = 0; i < rows.length; i += 1) {
            if (rows[i].querySelectorAll(".card-grid-news").length >= 2) {
                return rows[i];
            }
        }
        return null;
    }

    function init() {
        if (!isServicesPage()) return;
        var container = findContainer();
        if (!container) return;

        loadServices().then(function (services) {
            if (!services.length) return;
            var html = "";
            services.forEach(function (s, i) { html += buildCard(s, i); });
            container.innerHTML = html;

            if (window.SiteI18n && typeof window.SiteI18n.apply === "function") {
                window.SiteI18n.apply(container);
            }
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
