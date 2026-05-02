"""Admin panel helpers."""
from urllib.parse import urlencode

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def admin_lang_switch_url(context, lang_code: str) -> str:
    """Build current path + query with ?lang= set, preserving filters (excluding old lang)."""
    request = context["request"]
    pairs = [("lang", str(lang_code).lower())]
    for key, values in request.GET.lists():
        if key.lower() == "lang":
            continue
        pairs.extend((key, v) for v in values)
    return f"{request.path}?{urlencode(pairs)}"
