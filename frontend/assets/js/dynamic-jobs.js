/* Inter Labour - Dynamic job loader for the home page
 *
 * Replaces the hard-coded "Featured jobs" cards on the home page with live
 * data from the backend (/api/jobs/). Only admin-created jobs are shown - the
 * static placeholder cards are always cleared on init, even before the API
 * answers, so the home page never shows stale demo data.
 *
 * Triggers re-translation via window.SiteI18n.apply() after rendering.
 * Job cards intentionally omit WOW.js scroll classes — WOW sets
 * visibility:hidden until isVisible(); narrow viewports / resize often
 * left cards invisible while still in DOM.
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

    var CURRENCY_SYMBOLS = { EUR: "€", USD: "$", INR: "₹", GBP: "£" };
    function symbolFor(job) {
        if (job.currency_symbol) return job.currency_symbol;
        var code = (job.currency || "EUR").toString().toUpperCase();
        return CURRENCY_SYMBOLS[code] || code || "€";
    }

    function formatSalary(job) {
        var min = job.salary_min;
        var max = job.salary_max;
        var sym = symbolFor(job);
        if (!min && !max) return "";
        if (min && max) return sym + min + " – " + sym + max;
        return sym + (min || max);
    }

    function defaultImage() {
        return "/assets/imgs/page/job/digital.png";
    }

    function buildCard(job) {
        var title = job.title || "";
        var company = job.company_name || "Inter Labour";
        var location = job.location || "";
        var typeLabel = job.job_type_label || job.job_type || "Fulltime";
        var description = (job.description || "").toString();
        if (description.length > 220) description = description.slice(0, 220) + "…";
        var salary = formatSalary(job);
        var href = job.slug ? "/jobs/" + encodeURIComponent(job.slug) + "/" : "#";
        var image = job.image_url || defaultImage();
        var urgent = job.is_featured
            ? '<a href="#" class="btn btn-small background-urgent btn-pink mr-5">Spoedig</a>'
            : "";

        return (
            '<div class="col-lg-6 col-md-12 col-sm-12 col-12">' +
                '<div class="card-job hover-up il-dynamic-job-card">' +
                    '<div class="card-job-top">' +
                        '<div class="card-job-top--image">' +
                            '<a href="' + href + '"><figure><img alt="Inter Labour" src="' + escapeHtml(image) + '" /></figure></a>' +
                        '</div>' +
                        '<div class="card-job-top--info">' +
                            '<h6 class="card-job-top--info-heading"><a href="' + href + '">' + escapeHtml(title) + '</a></h6>' +
                            '<div class="row">' +
                                '<div class="col-md-9">' +
                                    '<a href="#"><span class="card-job-top--company">' + escapeHtml(company) + '</span></a>' +
                                    '<span class="card-job-top--location text-sm"><i class="fi-rr-marker"></i> ' + escapeHtml(location) + '</span>' +
                                    '<span class="card-job-top--type-job text-sm"><i class="fi-rr-briefcase"></i>' + escapeHtml(typeLabel) + '</span>' +
                                '</div>' +
                                (salary ? '<div class="col-md-3 text-md-end text-start"><span class="card-job-top--price">' + escapeHtml(salary) + '</span></div>' : "") +
                            '</div>' +
                        '</div>' +
                    '</div>' +
                    '<div class="card-job-description mt-20">' + escapeHtml(description) + '</div>' +
                    '<div class="card-job-bottom mt-25">' +
                        '<div class="row">' +
                            '<div class="col-lg-9 col-sm-8 col-12">' +
                                urgent +
                                '<a href="' + href + '" class="btn btn-small background-6 disc-btn">' + escapeHtml(typeLabel) + '</a>' +
                            '</div>' +
                            '<div class="col-lg-3 col-sm-4 col-12 text-end pt-5 pt-sm-15">' +
                                '<a href="#" class="text-lg color-muted"><i class="fi-rr-shield-check"></i></a>' +
                                '<a href="#" class="ml-5 text-lg color-muted"><i class="fi-rr-bookmark"></i></a>' +
                            '</div>' +
                        '</div>' +
                    '</div>' +
                '</div>' +
            '</div>'
        );
    }

    function isHomePage() {
        var p = window.location.pathname;
        return p === "/" || p === "/index.html" || p === "/index";
    }

    async function loadJobs() {
        try {
            var resp = await fetch("/api/jobs/?is_active=true&page_size=6", {
                headers: { "Accept": "application/json" }
            });
            if (!resp.ok) return [];
            var data = await resp.json();
            return Array.isArray(data) ? data : (data.results || []);
        } catch (_e) {
            return [];
        }
    }

    function renderInto(container, jobs) {
        if (!container) return;
        if (!jobs || jobs.length === 0) {
            container.innerHTML = (
                '<div class="row">' +
                    '<div class="col-12 text-center" style="padding:30px 0;color:#94a3b8;">' +
                        '<p>' + (window.SiteI18n && window.SiteI18n.getLang && window.SiteI18n.getLang() === "en"
                            ? "No jobs available right now."
                            : "Er zijn momenteel geen vacatures.") + '</p>' +
                    '</div>' +
                '</div>'
            );
            return;
        }
        var html = '<div class="row">';
        jobs.forEach(function (job) { html += buildCard(job); });
        html += "</div>";
        container.innerHTML = html;

        if (window.SiteI18n && typeof window.SiteI18n.apply === "function") {
            window.SiteI18n.apply(container);
        }
    }

    function clearStatic(container) {
        if (!container) return;
        container.innerHTML = (
            '<div class="row">' +
                '<div class="col-12 text-center" style="padding:30px 0;color:#94a3b8;">' +
                    '<p>...</p>' +
                '</div>' +
            '</div>'
        );
    }

    function init() {
        if (!isHomePage()) return;
        var container = document.querySelector(".list-recent-jobs.list-job-2-col");
        if (!container) return;
        clearStatic(container);
        loadJobs().then(function (jobs) {
            renderInto(container, jobs);
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
