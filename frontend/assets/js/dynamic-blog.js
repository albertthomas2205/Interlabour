/* Inter Labour - Dynamic blog loader
 *
 * Powers /blog.html (list) and /blog-detail.html?slug=xxx (single post)
 * by fetching from /api/blog-posts/.
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
        return "/assets/imgs/blog/blog-thumb-1.png";
    }

    function formatDate(iso) {
        if (!iso) return "";
        try {
            var d = new Date(iso);
            return d.toLocaleDateString();
        } catch (_e) {
            return iso.slice(0, 10);
        }
    }

    function isBlogListPage() {
        var p = window.location.pathname.toLowerCase();
        return p === "/blog.html" || p === "/blog/" || p === "/blog";
    }

    function isBlogDetailPage() {
        var p = window.location.pathname.toLowerCase();
        return p === "/blog-detail.html" || p === "/blog-single.html";
    }

    async function loadPosts() {
        try {
            var resp = await fetch("/api/blog-posts/?is_published=true&page_size=30", {
                headers: { "Accept": "application/json" }
            });
            if (!resp.ok) return [];
            var data = await resp.json();
            return Array.isArray(data) ? data : (data.results || []);
        } catch (_e) {
            return [];
        }
    }

    async function loadPostBySlug(slug) {
        try {
            var resp = await fetch("/api/blog-posts/?search=" + encodeURIComponent(slug) + "&page_size=50", {
                headers: { "Accept": "application/json" }
            });
            if (!resp.ok) return null;
            var data = await resp.json();
            var posts = Array.isArray(data) ? data : (data.results || []);
            for (var i = 0; i < posts.length; i += 1) {
                if (posts[i].slug === slug) return posts[i];
            }
            return posts[0] || null;
        } catch (_e) {
            return null;
        }
    }

    function buildCard(post) {
        var title = post.title || "";
        var excerpt = post.excerpt || "";
        if (!excerpt && post.content) {
            excerpt = post.content.replace(/<[^>]+>/g, "").slice(0, 180);
            if (post.content.length > 180) excerpt += "…";
        }
        var image = post.image_url || post.featured_image_url || defaultImage();
        var date = formatDate(post.published_at);
        var category = post.category_name || "";
        var detailUrl = "/blog-detail.html?slug=" + encodeURIComponent(post.slug || "");

        return (
            '<div class="col-lg-4 col-md-6 col-sm-12 col-12">' +
                '<div class="card-grid-news hover-up wow animate__animated animate__fadeIn">' +
                    '<div class="block-image-rd">' +
                        '<a href="' + detailUrl + '"><figure><img alt="' + escapeHtml(title) + '" src="' + escapeHtml(image) + '" /></figure></a>' +
                    '</div>' +
                    '<div class="card-info-bottom" style="padding:18px 16px;">' +
                        (category ? '<span style="font-size:11px;color:#3c65f5;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;">' + escapeHtml(category) + '</span>' : "") +
                        '<a href="' + detailUrl + '" style="display:block;margin:6px 0 10px;"><strong style="font-size:1.05rem;color:#05264e;">' + escapeHtml(title) + '</strong></a>' +
                        '<p class="text-gray-200" style="font-size:0.86rem;line-height:1.5;">' + escapeHtml(excerpt) + '</p>' +
                        '<div style="display:flex;justify-content:space-between;align-items:center;margin-top:14px;font-size:12px;color:#94a3b8;">' +
                            '<span>' + escapeHtml(post.author_name || "Inter Labour") + '</span>' +
                            '<span>' + escapeHtml(date) + '</span>' +
                        '</div>' +
                    '</div>' +
                '</div>' +
            '</div>'
        );
    }

    function renderList(posts) {
        var container = document.getElementById("blog-list");
        if (!container) return;
        if (!posts.length) {
            var lang = window.SiteI18n && window.SiteI18n.getLang ? window.SiteI18n.getLang() : "nl";
            container.innerHTML = '<div class="col-12 text-center" style="padding:60px 0;color:#94a3b8;">' +
                (lang === "en" ? "<p>No blog posts yet.</p>" : "<p>Er zijn nog geen blogberichten.</p>") +
                '</div>';
            return;
        }
        var html = "";
        posts.forEach(function (p) { html += buildCard(p); });
        container.innerHTML = html;
        if (window.SiteI18n && typeof window.SiteI18n.apply === "function") {
            window.SiteI18n.apply(container);
        }
    }

    function renderDetail(post) {
        var container = document.getElementById("blog-detail");
        if (!container) return;
        if (!post) {
            var lang = window.SiteI18n && window.SiteI18n.getLang ? window.SiteI18n.getLang() : "nl";
            container.innerHTML = '<div style="padding:60px 0;text-align:center;color:#94a3b8;">' +
                (lang === "en" ? "<h3>Post not found.</h3>" : "<h3>Bericht niet gevonden.</h3>") +
                '<p><a href="/blog.html" class="btn btn-default mt-20">← Blog</a></p></div>';
            return;
        }
        var image = post.image_url || post.featured_image_url || defaultImage();
        var date = formatDate(post.published_at);
        var content = post.content || "";

        document.title = "Inter Labour – " + (post.title || "");

        container.innerHTML = (
            '<article class="blog-post">' +
                (image ? '<figure style="margin:0 0 24px;border-radius:14px;overflow:hidden;"><img src="' + escapeHtml(image) + '" alt="' + escapeHtml(post.title || "") + '" style="width:100%;display:block;" /></figure>' : "") +
                (post.category_name ? '<span style="font-size:12px;color:#3c65f5;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;">' + escapeHtml(post.category_name) + '</span>' : "") +
                '<h1 style="font-size:2rem;color:#05264e;margin:8px 0 14px;">' + escapeHtml(post.title || "") + '</h1>' +
                '<div style="font-size:13px;color:#94a3b8;margin-bottom:24px;">' +
                    escapeHtml(post.author_name || "Inter Labour") + ' • ' + escapeHtml(date) +
                '</div>' +
                '<div class="blog-content" style="font-size:1rem;color:#384152;line-height:1.7;">' +
                    content.replace(/\n/g, "<br />") +
                '</div>' +
                '<div style="margin-top:36px;"><a href="/blog.html" class="btn btn-border">← Blog</a></div>' +
            '</article>'
        );

        if (window.SiteI18n && typeof window.SiteI18n.apply === "function") {
            window.SiteI18n.apply(container);
        }
    }

    function init() {
        if (isBlogListPage()) {
            loadPosts().then(renderList);
            return;
        }
        if (isBlogDetailPage()) {
            var params = new URLSearchParams(window.location.search);
            var slug = params.get("slug");
            if (!slug) { renderDetail(null); return; }
            loadPostBySlug(slug).then(renderDetail);
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
