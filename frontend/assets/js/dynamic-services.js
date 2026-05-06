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
        // Accept common static routes + any path containing page-service
        // (e.g. /page-service.html, /pages/page-service.html).
        return (
            p.indexOf("page-service") !== -1 ||
            p === "/page-services.html" ||
            p.endsWith("/services") ||
            p.endsWith("/services/")
        );
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
        var explicit = document.getElementById("services-grid");
        if (explicit) return explicit;

        var rows = document.querySelectorAll(".section-box .row.mt-100");
        for (var i = 0; i < rows.length; i += 1) {
            if (rows[i].querySelectorAll(".card-grid-news").length >= 2) {
                return rows[i];
            }
        }
        return null;
    }

    function init() {
        var container = findContainer();
        if (!container) return;
        // If the explicit container is present, render regardless of path.
        if (!isServicesPage() && container.id !== "services-grid") return;

        // Avoid duplicate fetch/render when both auth-integration injection and an explicit script tag load this file.
        if (window.__ilServicesHydrated === "1") return;
        window.__ilServicesHydrated = "1";

        loadServices()
            .then(function (services) {
                var html = "";
                if (!services.length) {
                    html =
                        '<div class="col-12">' +
                            '<div class="text-center" style="padding:24px 0;color:#6b7280;">' +
                                '<p>No services available.</p>' +
                            '</div>' +
                        '</div>';
                } else {
                    services.forEach(function (s, i) {
                        html += buildCard(s, i);
                    });
                }
                container.innerHTML = html;

                if (window.SiteI18n && typeof window.SiteI18n.apply === "function") {
                    window.SiteI18n.apply(container);
                }
            })
            .catch(function () {
                container.innerHTML =
                    '<div class="col-12">' +
                        '<div class="text-center" style="padding:24px 0;color:#6b7280;">' +
                            '<p>No services available.</p>' +
                        '</div>' +
                    '</div>';
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
