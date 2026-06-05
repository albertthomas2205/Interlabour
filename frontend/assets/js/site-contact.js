/* Inter Labour — site-wide contact details (phone shown on every page). */
(function () {
    "use strict";

    var PHONE_DISPLAY = "+91 7559999161";
    var PHONE_TEL = "+917559999161";

    function phoneLinkHtml() {
        return '<a href="tel:' + PHONE_TEL + '" class="site-phone-link">' + PHONE_DISPLAY + "</a>";
    }

    function injectFooterPhone() {
        var phoneBlock =
            '<p class="site-phone mt-15 mb-0" data-site-phone="1">' + phoneLinkHtml() + "</p>";
        var cols = document.querySelectorAll(
            "footer .footer-brand-col, footer .col-md-4.col-sm-12, footer .row > .col-md-4:first-child"
        );
        for (var i = 0; i < cols.length; i += 1) {
            var col = cols[i];
            if (!col.closest("footer")) continue;
            if (col.querySelector("[data-site-phone='1']")) continue;
            var anchor = col.querySelector(".mt-20.mb-20") || col.querySelector("div.mt-20") || col.querySelector("img");
            if (anchor) {
                anchor.insertAdjacentHTML("afterend", phoneBlock);
            } else {
                col.insertAdjacentHTML("beforeend", phoneBlock);
            }
        }
    }

    function normalizeLegacyPhones(root) {
        var node = root || document.body;
        if (!node) return;

        var legacyPatterns = [
            /\(\+31\)\s*456-7890/gi,
            /\(123\)\s*456-7890/gi,
            /\+\s*31\s*654-430-309/gi,
            /\+\s*31\s*6532-430-309/gi,
            /\+\s*48\s*654-430-309/gi,
            /\+\s*1\s*6532-430-309/gi,
            /\(\+91\)\s*-\s*540-025-124553/gi
        ];

        var slots = node.querySelectorAll("[data-site-phone]");
        for (var s = 0; s < slots.length; s += 1) {
            if (!slots[s].querySelector("a")) {
                slots[s].innerHTML = phoneLinkHtml();
            }
        }

        var abbrs = node.querySelectorAll('abbr[title="Phone"]');
        for (var a = 0; a < abbrs.length; a += 1) {
            var parent = abbrs[a].parentNode;
            if (!parent) continue;
            var html = parent.innerHTML;
            var changed = false;
            for (var p = 0; p < legacyPatterns.length; p += 1) {
                if (legacyPatterns[p].test(html)) {
                    html = html.replace(legacyPatterns[p], phoneLinkHtml());
                    changed = true;
                }
                legacyPatterns[p].lastIndex = 0;
            }
            if (changed) parent.innerHTML = html;
        }

        var headsetSpans = node.querySelectorAll(".fi-rr-headset");
        for (var h = 0; h < headsetSpans.length; h += 1) {
            var wrap = headsetSpans[h].parentElement;
            if (!wrap) continue;
            var span = wrap.querySelector("span span") || wrap.querySelector("span:last-child");
            if (span) span.innerHTML = phoneLinkHtml();
        }
    }

    function init() {
        normalizeLegacyPhones(document.body);
        injectFooterPhone();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }

    window.SiteContact = {
        phone: PHONE_DISPLAY,
        tel: PHONE_TEL,
        linkHtml: phoneLinkHtml
    };
})();
