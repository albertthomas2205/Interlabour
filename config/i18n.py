from django.conf import settings
from django.utils import translation


SUPPORTED_LANGUAGES = {code for code, _ in getattr(settings, "LANGUAGES", [])}
DEFAULT_LANGUAGE = getattr(settings, "LANGUAGE_CODE", "nl") or "nl"
LANG_COOKIE_NAME = "il_lang"


class QueryStringSessionLanguageMiddleware:
    """Owns language selection for the whole project.

    Resolution order, highest priority first:
        1. ``?lang=nl|en`` query parameter (also persisted to session/cookie)
        2. session value
        3. ``il_lang`` cookie
        4. ``LANGUAGE_CODE`` setting (default ``nl``)

    The selected language is activated for Django's i18n machinery (templates,
    DRF serializers, model accessors via ``get_language()``) and is exposed on
    ``request.LANGUAGE_CODE``. We intentionally replace Django's
    ``LocaleMiddleware`` so this is the single source of truth.
    """

    SESSION_KEY = "lang"
    QUERY_KEY = "lang"

    def __init__(self, get_response):
        self.get_response = get_response

    def _resolve(self, request) -> tuple[str, bool]:
        explicit = (request.GET.get(self.QUERY_KEY) or "").strip().lower()
        if explicit in SUPPORTED_LANGUAGES:
            return explicit, True

        session_value = None
        try:
            session_value = request.session.get(self.SESSION_KEY)
        except Exception:
            session_value = None
        if session_value in SUPPORTED_LANGUAGES:
            return session_value, False

        cookie_value = (request.COOKIES.get(LANG_COOKIE_NAME) or "").strip().lower()
        if cookie_value in SUPPORTED_LANGUAGES:
            return cookie_value, False

        return (DEFAULT_LANGUAGE if DEFAULT_LANGUAGE in SUPPORTED_LANGUAGES else "nl"), False

    def __call__(self, request):
        lang, persist = self._resolve(request)

        translation.activate(lang)
        request.LANGUAGE_CODE = lang

        if persist:
            try:
                request.session[self.SESSION_KEY] = lang
            except Exception:
                pass

        response = self.get_response(request)

        if persist:
            response.set_cookie(LANG_COOKIE_NAME, lang, max_age=60 * 60 * 24 * 365)

        translation.deactivate()
        return response
