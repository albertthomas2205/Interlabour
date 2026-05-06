/* Inter Labour - Static page bilingual support (NL <-> EN)
 *
 * - Default language: Dutch (nl)
 * - Adds NL/EN toggle button to the header on every page
 * - Persists choice via localStorage
 * - Translates header / forms / body / footer between Dutch and English
 *   without changing UI structure or styling.
 *
 * Add new ENTRIES to extend coverage. Each entry is a paired { nl, en } string.
 * Translation walks all visible text nodes and looks up the trimmed value
 * in the active language's dictionary; if not present the text is left as-is.
 */
(function () {
    "use strict";

    var STORAGE_KEY = "site_lang";
    var DEFAULT_LANG = "nl";

    // -------------------------------------------------------------------
    // Translation entries (single source of truth - both directions built from this)
    // -------------------------------------------------------------------
    var ENTRIES = [
        // Header / navigation
        { en: "Home", nl: "Home" },
        { en: "About Us", nl: "Over Ons" },
        { en: "About", nl: "Over" },
        { en: "about", nl: "over" },
        { en: "Services", nl: "Diensten" },
        { en: "Service", nl: "Dienst" },
        { en: "Jobs", nl: "Vacatures" },
        { en: "jobs", nl: "vacatures" },
        { en: "Contact", nl: "Contact" },
        { en: "Contact Us", nl: "Neem Contact Op" },
        { en: "Search for items…", nl: "Zoek items…" },

        // Auth links / titles
        { en: "Login", nl: "Inloggen" },
        { en: "Sign In", nl: "Inloggen" },
        { en: "Sign in", nl: "Inloggen" },
        { en: "Register", nl: "Registreren" },
        { en: "Logout", nl: "Uitloggen" },
        { en: "Create Account", nl: "Account Aanmaken" },
        { en: "Create account", nl: "Account aanmaken" },
        { en: "Admin Panel", nl: "Beheerderspaneel" },
        { en: "Use your registered email and password.", nl: "Gebruik uw geregistreerde e-mail en wachtwoord." },
        { en: "Register with your email. We will send an OTP for verification.", nl: "Registreer met uw e-mail. We sturen een OTP ter verificatie." },
        { en: "Email address", nl: "E-mailadres" },
        { en: "Password", nl: "Wachtwoord" },
        { en: "Confirm password", nl: "Bevestig wachtwoord" },
        { en: "First name", nl: "Voornaam" },
        { en: "Last name", nl: "Achternaam" },
        { en: "New here?", nl: "Nieuw hier?" },
        { en: "Already have an account?", nl: "Heeft u al een account?" },
        { en: "Note: If your email is not verified yet, complete OTP verification first.", nl: "Let op: Als uw e-mail nog niet is geverifieerd, voltooi eerst de OTP-verificatie." },
        { en: "Verify Email OTP", nl: "Verifieer E-mail OTP" },
        { en: "Verify OTP", nl: "Verifieer OTP" },
        { en: "Resend OTP", nl: "OTP opnieuw versturen" },
        { en: "Enter the OTP sent to your email address.", nl: "Voer de OTP in die naar uw e-mailadres is gestuurd." },
        { en: "6-digit OTP", nl: "6-cijferige OTP" },
        { en: "Back to", nl: "Terug naar" },
        { en: "If SMTP is not configured, OTP appears in the Django server console.", nl: "Als SMTP niet is geconfigureerd, verschijnt de OTP in de Django-serverconsole." },
        { en: "Creating account...", nl: "Account aanmaken..." },

        // Forgot / Reset password pages
        { en: "Forgot Password", nl: "Wachtwoord vergeten" },
        { en: "Forgot password?", nl: "Wachtwoord vergeten?" },
        { en: "Reset Password", nl: "Wachtwoord opnieuw instellen" },
        { en: "Enter your registered email address and we will send you a 6-digit code to reset your password.",
          nl: "Voer uw geregistreerde e-mailadres in en wij sturen u een 6-cijferige code om uw wachtwoord opnieuw in te stellen." },
        { en: "Enter the 6-digit code from your email and choose a new password.",
          nl: "Voer de 6-cijferige code uit uw e-mail in en kies een nieuw wachtwoord." },
        { en: "Send Reset Code", nl: "Resetcode versturen" },
        { en: "Update Password", nl: "Wachtwoord bijwerken" },
        { en: "Resend Code", nl: "Code opnieuw versturen" },
        { en: "Remembered it?", nl: "Weet u het weer?" },
        { en: "Wrong email?", nl: "Verkeerd e-mailadres?" },
        { en: "Start over", nl: "Opnieuw beginnen" },
        { en: "6-digit code", nl: "6-cijferige code" },
        { en: "New password (min. 8 characters)", nl: "Nieuw wachtwoord (min. 8 tekens)" },
        { en: "Note: If SMTP is not configured, the OTP will appear in the Django server console.",
          nl: "Let op: Als SMTP niet is geconfigureerd, verschijnt de OTP in de Django-serverconsole." },

        // Page titles
        { en: "Inter Labour - Forgot Password", nl: "Inter Labour - Wachtwoord vergeten" },
        { en: "Inter Labour - Reset Password", nl: "Inter Labour - Wachtwoord opnieuw instellen" },

        // Dynamic auth-form messages (login / register / verify / forgot / reset)
        { en: "Email and password are required.", nl: "E-mailadres en wachtwoord zijn verplicht." },
        { en: "Passwords do not match.", nl: "Wachtwoorden komen niet overeen." },
        { en: "Registration successful. OTP sent to your email.", nl: "Registratie geslaagd. OTP is naar uw e-mail verzonden." },
        { en: "Email and OTP are required.", nl: "E-mailadres en OTP zijn verplicht." },
        { en: "Verifying...", nl: "Verifiëren..." },
        { en: "Email verified successfully. Redirecting to login...", nl: "E-mail succesvol geverifieerd. Doorverwijzen naar inloggen..." },
        { en: "Enter your email first.", nl: "Voer eerst uw e-mailadres in." },
        { en: "Sending...", nl: "Versturen..." },
        { en: "OTP sent again. Please check your email.", nl: "OTP opnieuw verstuurd. Controleer uw e-mail." },
        { en: "Please provide email and password.", nl: "Geef e-mailadres en wachtwoord op." },
        { en: "Signing in...", nl: "Inloggen..." },
        { en: "Login successful. Redirecting...", nl: "Inloggen geslaagd. Doorverwijzen..." },
        { en: "Please enter your email address.", nl: "Voer uw e-mailadres in." },
        { en: "Reset code sent. Redirecting...", nl: "Resetcode verzonden. Doorverwijzen..." },
        { en: "Email is required.", nl: "E-mailadres is verplicht." },
        { en: "Enter the 6-digit code from your email.", nl: "Voer de 6-cijferige code uit uw e-mail in." },
        { en: "Password must be at least 8 characters.", nl: "Wachtwoord moet minimaal 8 tekens bevatten." },
        { en: "Updating...", nl: "Bijwerken..." },
        { en: "Password updated successfully. Redirecting to login...", nl: "Wachtwoord succesvol bijgewerkt. Doorverwijzen naar inloggen..." },
        { en: "A new reset code has been sent.", nl: "Een nieuwe resetcode is verzonden." },
        { en: "Something went wrong. Please try again.", nl: "Er is iets misgegaan. Probeer het opnieuw." },
        { en: "Session expired. Please sign in again.", nl: "Sessie verlopen. Log opnieuw in." },

        // Hero / homepage
        { en: "Welcome to", nl: "Welkom bij" },
        { en: "Inter Labour specialises in international recruitment, staffing and workforce solutions. We bridge qualified talent with global opportunities.",
          nl: "Inter Labour is gespecialiseerd in internationale recruitment, personeelsvoorziening en workforce-oplossingen. Wij slaan de brug tussen gekwalificeerd talent en wereldwijde kansen." },
        { en: "Explore more", nl: "Ontdek meer" },
        { en: "View more", nl: "Bekijk meer" },
        { en: "Who We Are", nl: "Wie Wij Zijn" },
        { en: "Inter Labour is an international recruitment and staffing company that helps organisations find the right employees, worldwide. We specialise in hiring both skilled and unskilled personnel for various sectors.",
          nl: "Inter Labour is een internationaal recruitment- en personeelsbedrijf dat organisaties helpt bij het vinden van de juiste medewerkers, wereldwijd. Wij zijn gespecialiseerd in het werven van zowel gekwalificeerd als ongeschoold personeel voor diverse sectoren." },
        { en: "With a strong network and broad expertise, we support companies in building efficient teams while creating valuable career opportunities for candidates.",
          nl: "Met een sterk netwerk en uitgebreide expertise ondersteunen wij bedrijven bij het opbouwen van efficiënte teams en creëren wij tegelijkertijd waardevolle carrièremogelijkheden voor kandidaten." },

        { en: "Featured jobs", nl: "Uitgelichte vacatures" },
        { en: "The #1 global recruitment partner for your staffing needs", nl: "De #1 wereldwijde recruitmentpartner voor uw personeelsbehoeften" },
        { en: "Find Your Next Job", nl: "Vind Uw Volgende Baan" },
        { en: "Discover international vacancies and build your career with Inter Labour", nl: "Ontdek internationale vacatures en bouw uw carrière met Inter Labour" },
        { en: "Our Jobs", nl: "Onze Vacatures" },

        // Job cards
        { en: "Farm Worker", nl: "Landarbeider" },
        { en: "Inter Labour", nl: "Inter labour" },
        { en: "Full time", nl: "Fulltime" },
        { en: "Urgent", nl: "Spoedig" },
        { en: "We are looking for motivated and reliable farm workers to support agricultural activities. The role includes helping with planting, harvesting and maintaining crops, as well as general farm work.",
          nl: "Wij zijn op zoek naar gemotiveerde en betrouwbare farmmedewerkers ter ondersteuning van agrarische werkzaamheden. De functie omvat het helpen bij het planten, oogsten en onderhouden van gewassen, evenals algemene werkzaamheden op de boerderij." },

        // Testimonials / blog
        { en: "What Our Clients Say", nl: "Wat Onze Klanten Zeggen" },
        { en: "Trusted by companies and candidates worldwide for reliable recruitment and staffing solutions.",
          nl: "Vertrouwd door bedrijven en kandidaten wereldwijd voor betrouwbare recruitment- en personeelsoplossingen." },
        { en: "Inter Labour quickly and efficiently helped us find qualified staff. The whole process was professional and smooth.",
          nl: "Inter Labour heeft ons snel en efficiënt geholpen bij het vinden van gekwalificeerd personeel. Het hele proces verliep professioneel en soepel." },
        { en: "Operations Manager, Construction Company", nl: "Operations Manager, Bouwbedrijf" },
        { en: "Our blogs", nl: "Onze blogs" },
        { en: "Latest news and events", nl: "Laatste nieuws en evenementen" },
        { en: "How to Get an Unskilled Job Abroad: Step-by-Step Guide", nl: "Hoe Krijg Je een Ongeschoolde Baan in het Buitenland: Stapsgewijze Gids" },
        { en: "Keep reading", nl: "Doorlezen" },

        // Newsletter
        { en: "Sign up to", nl: "Meld je aan om" },
        { en: "receive the latest vacancies", nl: "de nieuwste vacatures te ontvangen" },
        { en: "Subscribe", nl: "Abonneren" },

        // Filter / sidebar
        { en: "Set a job alert", nl: "Stel een vacatureherinnering in" },
        { en: "Enter your email and receive job notifications.", nl: "Voer uw e-mailadres in en ontvang vacaturemeldingen." },
        { en: "Enter your email address.", nl: "Voer uw e-mailadres in." },
        { en: "Submit", nl: "Indienen" },
        { en: "Location", nl: "Locatie" },
        { en: "Category", nl: "categorie" },
        { en: "Experience levels", nl: "Ervaringsniveaus" },
        { en: "Salary range", nl: "Salarisbereik" },
        { en: "Apply filter", nl: "Filter toepassen" },
        { en: "Reset filter", nl: "Filter resetten" },
        { en: "Are you ready?", nl: "Bent u klaar??" },
        { en: "Partner with Inter Labour for trusted recruitment and international opportunities", nl: "Werk samen met Inter Labour voor betrothal recruitment en internationale kansen" },
        { en: "Apply now", nl: "Solliciteer nu" },
        { en: "Job type", nl: "Job type" },
        { en: "Full-time Jobs", nl: "Fulltime Banen" },
        { en: "Part-time Jobs", nl: "Parttime Banen" },
        { en: "Contract Jobs", nl: "Contractbanen" },
        { en: "Temporary Jobs", nl: "Tijdelijke Banen" },
        { en: "Seasonal Work", nl: "Seizoenswerk" },
        { en: "Production & Factory", nl: "Productie & Fabriek" },
        { en: "Production Worker", nl: "Productiemedewerker" },
        { en: "Agriculture", nl: "Landbouw" },
        { en: "Construction", nl: "Bouw" },
        { en: "Entry level", nl: "Instapniveau" },
        { en: "Beginner", nl: "Beginner" },
        { en: "Mid level", nl: "Gemiddeld Niveau" },
        { en: "Experienced", nl: "Ervaren" },
        { en: "Supervisor level", nl: "Supervisor Niveau" },
        { en: "Specialised", nl: "Gespecialiseerd" },

        // Job single page
        { en: "KEY RESPONSIBILITIES", nl: "BELANGRIJKSTE TAKEN" },
        { en: "REQUIREMENTS", nl: "VEREISTEN" },
        { en: "BENEFITS", nl: "VOORDELEN" },
        { en: "Job type", nl: "Soort baan" },
        { en: "Salary", nl: "Salaris" },
        { en: "Recent jobs", nl: "Recente vacatures" },
        { en: "Share", nl: "Delen" },
        { en: "Tweet", nl: "Tweet" },
        { en: "Pin", nl: "Pin" },
        { en: "Results", nl: "Resultaten" },
        { en: "of", nl: "van" },
        { en: "jobs", nl: "banen" },
        { en: "Sort by:", nl: "Sorteren op:" },
        { en: "Newest posts", nl: "Nieuwste berichten" },
        { en: "Oldest posts", nl: "Oudste berichten" },
        { en: "Rate posts", nl: "Berichten beoordelen" },

        // Contact
        { en: "Get In Touch", nl: "Neem Contact Op" },
        { en: "We are ready to help you with your staffing and career needs", nl: "Wij staan klaar om u te helpen met uw personeels- en carrièrebehoeften" },
        { en: "Office address", nl: "Kantooradres" },
        { en: "Send message", nl: "Bericht verzenden" },
        { en: "Contact us", nl: "Neem contact met ons op" },
        { en: "Your email address will not be published. Required fields are marked with *.", nl: "Uw e-mailadres wordt niet gepubliceerd. Vereiste velden zijn gemarkeerd met een *." },
        { en: "Phone", nl: "Telefoon" },
        { en: "Email", nl: "e-mail" },
        { en: "Address", nl: "adres" },
        { en: "First name", nl: "Voornaam" },
        { en: "Your email address", nl: "Uw e-mailadres" },
        { en: "Your phone number", nl: "Uw telefoonnummer" },
        { en: "Subject", nl: "Onderwerp" },
        { en: "Message", nl: "Bericht" },
        { en: "View map", nl: "Bekijk kaart" },

        // Footer
        { en: "Company", nl: "Bedrijf" },
        { en: "About us", nl: "Over ons" },
        { en: "Our Services", nl: "Onze Diensten" },
        { en: "Job List", nl: "Vacaturelijst" },
        { en: "General Worker", nl: "Algemene Arbeider" },
        { en: "Construction Assistant", nl: "Bouwassistent" },
        { en: "Mason Assistant", nl: "Metselaar Assistent" },
        { en: "Scaffolding Assistant", nl: "Steigerbouw Assistent" },
        { en: "Logistics & Warehouse", nl: "Logistiek & Magazijn" },
        { en: "Warehouse Worker", nl: "Magazijnmedewerker" },
        { en: "Packing & Sorting Worker", nl: "Inpak- en Sorteermedewerker" },
        { en: "Loading & Unloading Worker", nl: "Laad- en Losmedewerker" },
        { en: "Delivery Assistant", nl: "Bezorg Assistent" },
        { en: "Support", nl: "Ondersteuning" },
        { en: "Privacy policy", nl: "Privacybeleid" },
        { en: "Helpdesk", nl: "Helpdesk" },
        { en: "Terms & conditions", nl: "Algemene voorwaarden" },
        { en: "FAQ", nl: "Veelgestelde vragen" },
        { en: "All Rights Reserved", nl: "Alle rechten voorbehouden" },
        { en: "Inter Labour is an international recruitment and staffing company that helps organisations find the right employees, worldwide.",
          nl: "Inter Labour is een internationaal recruitment- en personeelsbedrijf dat organisaties helpt bij het vinden van de juiste medewerkers, wereldwijd." },

        // Misc
        { en: "Search", nl: "Zoeken" },
        { en: "Search jobs", nl: "Zoek vacatures" },
        { en: "No jobs found.", nl: "Geen vacatures gevonden." },
        { en: "No services available.", nl: "Geen diensten beschikbaar." },

        // My Account page
        { en: "My Account", nl: "Mijn Account" },
        { en: "Profile information", nl: "Profielinformatie" },
        { en: "Settings", nl: "Instellingen" },
        { en: "Close", nl: "Sluiten" },
        { en: "Change password", nl: "Wachtwoord wijzigen" },
        { en: "New password", nl: "Nieuw wachtwoord" },
        { en: "Confirm new password", nl: "Bevestig nieuw wachtwoord" },
        { en: "Update password", nl: "Wachtwoord bijwerken" },
        { en: "My CV / Resume", nl: "Mijn CV / Cv" },
        { en: "Drag & drop your CV here, or", nl: "Sleep uw CV hierheen, of" },
        { en: "browse to upload", nl: "klik om te uploaden" },
        { en: "Accepted formats: PDF, DOC, DOCX. Max 5 MB.", nl: "Toegestane formaten: PDF, DOC, DOCX. Max. 5 MB." },
        { en: "Current CV:", nl: "Huidig cv:" },
        { en: "Download", nl: "Downloaden" },
        { en: "Save changes", nl: "Wijzigingen opslaan" },
        { en: "Cancel", nl: "Annuleren" },
        { en: "My applications", nl: "Mijn sollicitaties" },
        { en: "You haven't applied to any jobs yet.", nl: "U heeft zich nog niet aangemeld voor een vacature." },
        { en: "Browse more jobs", nl: "Meer vacatures bekijken" },
        { en: "Browse Jobs", nl: "Vacatures bekijken" },
        { en: "Member since", nl: "Lid sinds" },
        { en: "Applications", nl: "Sollicitaties" },
        { en: "Quick links", nl: "Snelle links" },
        { en: "User", nl: "Gebruiker" },
        { en: "Privacy Policy", nl: "Privacybeleid" },
        { en: "Help Desk", nl: "Helpdesk" },
        { en: "Terms & Conditions", nl: "Algemene voorwaarden" },
        { en: "All Rights Reserved", nl: "Alle rechten voorbehouden" }
    ];

    // Build dictionaries
    var DICT = { nl: {}, en: {} };
    ENTRIES.forEach(function (e) {
        if (e.en && e.nl) {
            DICT.nl[e.en] = e.nl; // English source -> Dutch
            DICT.en[e.nl] = e.en; // Dutch source -> English
        }
    });

    /* Read the il_lang cookie that Django middleware sets (authoritative source).
       Fall back to localStorage for cases where the cookie hasn't been set yet. */
    function getCookie(name) {
        var m = document.cookie.match(new RegExp("(?:^|;\\s*)" + name + "=([^;]*)"));
        return m ? decodeURIComponent(m[1]) : null;
    }

    function getLang() {
        var fromCookie = getCookie("il_lang");
        if (fromCookie === "en" || fromCookie === "nl") return fromCookie;
        try {
            var v = localStorage.getItem(STORAGE_KEY);
            return v === "en" ? "en" : "nl";
        } catch (_e) { return DEFAULT_LANG; }
    }
    function setLang(lang) {
        try { localStorage.setItem(STORAGE_KEY, lang); } catch (_e) {}
    }

    var SKIP_TAGS = { SCRIPT: 1, STYLE: 1, NOSCRIPT: 1, IFRAME: 1, CODE: 1, PRE: 1, TEXTAREA: 1 };

    function walk(node, fn) {
        if (!node) return;
        if (node.nodeType === 3) { fn(node); return; }
        if (node.nodeType !== 1) return;
        if (SKIP_TAGS[node.tagName]) return;
        if (node.dataset && node.dataset.i18nSkip) return;
        var child = node.firstChild;
        while (child) {
            var next = child.nextSibling;
            walk(child, fn);
            child = next;
        }
    }

    function lookup(text, dict) {
        var trimmed = text.replace(/\s+/g, " ").trim();
        if (!trimmed) return null;
        return Object.prototype.hasOwnProperty.call(dict, trimmed) ? dict[trimmed] : null;
    }

    function applyTo(root, dict) {
        if (!root) return;
        walk(root, function (textNode) {
            var translated = lookup(textNode.nodeValue, dict);
            if (translated !== null) {
                // preserve surrounding whitespace
                var match = textNode.nodeValue.match(/^(\s*)([\s\S]*?)(\s*)$/);
                var lead = match ? match[1] : "";
                var trail = match ? match[3] : "";
                textNode.nodeValue = lead + translated + trail;
            }
        });

        // Translate input placeholders
        var ph = root.querySelectorAll ? root.querySelectorAll("input[placeholder], textarea[placeholder]") : [];
        for (var i = 0; i < ph.length; i++) {
            var v = ph[i].getAttribute("placeholder");
            if (v) {
                var tr = lookup(v, dict);
                if (tr !== null) ph[i].setAttribute("placeholder", tr);
            }
        }

        // Translate titles
        var titled = root.querySelectorAll ? root.querySelectorAll("[title]") : [];
        for (var j = 0; j < titled.length; j++) {
            var t = titled[j].getAttribute("title");
            var trt = lookup(t, dict);
            if (trt !== null) titled[j].setAttribute("title", trt);
        }
    }

    function applyLang(lang) {
        var dict = DICT[lang] || DICT.nl;
        applyTo(document.body, dict);
        if (document.title) {
            var tr = lookup(document.title, dict);
            if (tr !== null) document.title = tr;
        }
        document.documentElement.setAttribute("lang", lang);
    }

    // Public re-application hook (used by dynamic content loaders)
    function reapply(root) {
        applyTo(root || document.body, DICT[getLang()] || DICT.nl);
    }

    function injectToggle() {
        var nav =
            document.querySelector(".main-header .header-left .header-nav .main-menu") ||
            document.querySelector(".main-header") ||
            document.querySelector("header") ||
            document.body;
        if (!nav) return;
        if (document.getElementById("site-lang-toggle")) return;

        var wrap = document.createElement("div");
        wrap.id = "site-lang-toggle";
        wrap.setAttribute("data-i18n-skip", "1");
        wrap.style.cssText = [
            "display:inline-flex",
            "align-items:center",
            "gap:0",
            "border:1px solid rgba(0,0,0,0.1)",
            "background:#fff",
            "padding:3px",
            "border-radius:999px",
            "box-shadow:0 4px 12px rgba(15,23,42,0.06)",
            "vertical-align:middle"
        ].join(";");

        function makeBtn(code, label) {
            var b = document.createElement("button");
            b.type = "button";
            b.textContent = label;
            b.dataset.lang = code;
            b.style.cssText = [
                "border:0",
                "background:transparent",
                "color:#0f172a",
                "padding:6px 12px",
                "font-size:12px",
                "font-weight:700",
                "border-radius:999px",
                "cursor:pointer",
                "letter-spacing:0.04em",
                "font-family:inherit"
            ].join(";");
            return b;
        }
        var nlBtn = makeBtn("nl", "NL");
        var enBtn = makeBtn("en", "EN");
        wrap.appendChild(nlBtn);
        wrap.appendChild(enBtn);

        function paint() {
            var current = getLang();
            [nlBtn, enBtn].forEach(function (btn) {
                if (btn.dataset.lang === current) {
                    btn.style.background = "linear-gradient(135deg,#19263f,#2d467a)";
                    btn.style.color = "#fff";
                    btn.style.boxShadow = "0 4px 12px rgba(25,38,63,0.35)";
                } else {
                    btn.style.background = "transparent";
                    btn.style.color = "#475569";
                    btn.style.boxShadow = "none";
                }
            });
        }
        function onClick(lang) {
            return function () {
                if (getLang() === lang) return;
                setLang(lang); // sync localStorage immediately
                // Navigate with ?lang= so Django middleware updates the server-side
                // session + il_lang cookie and re-renders {% trans %} content correctly.
                try {
                    var url = new URL(window.location.href);
                    url.searchParams.set("lang", lang);
                    window.location.href = url.toString();
                } catch (_e) {
                    // Fallback for very old browsers: just do client-side translation
                    applyLang(lang);
                    paint();
                }
            };
        }
        nlBtn.addEventListener("click", onClick("nl"));
        enBtn.addEventListener("click", onClick("en"));
        paint();

        var langTarget = document.getElementById("header-lang");
        if (langTarget) {
            langTarget.appendChild(wrap);
        } else {
            var menu = document.querySelector(".main-header .header-nav .main-menu");
            if (menu) {
                var li = document.createElement("li");
                li.style.cssText = "display:flex;align-items:center;";
                li.setAttribute("data-i18n-skip", "1");
                li.appendChild(wrap);
                menu.appendChild(li);
            } else {
                nav.appendChild(wrap);
            }
        }
    }

    function init() {
        // Remove ?lang= from the URL after the server has already read and stored it,
        // so it doesn't linger visibly in the address bar.
        try {
            var url = new URL(window.location.href);
            if (url.searchParams.has("lang")) {
                url.searchParams.delete("lang");
                history.replaceState(null, "", url.pathname + (url.search || "") + (url.hash || ""));
            }
        } catch (_e) {}

        injectToggle();
        // Always apply translations on load (default NL translates English source to Dutch).
        applyLang(getLang());
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }

    // Expose for dynamic content loaders
    window.SiteI18n = {
        getLang: getLang,
        apply: function (root) { reapply(root); },
        translate: translateString
    };
})();
