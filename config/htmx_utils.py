"""Небольшие помощники для модальных окон на HTMX.

Модалки живут в #modal-root (см. templates/base.html). Любой GET на
модальный view отдаёт фрагмент, обёрнутый в templates/modal_base.html
(затемнение + карточка). После успешного сохранения нужен не обычный
редирект (htmx подставил бы HTML целевой страницы прямо в #modal-root),
а HX-Redirect — по нему htmx делает полноценный переход браузера, и
модалка естественным образом закрывается вместе со сменой страницы.
"""

from django.http import HttpResponse


def htmx_redirect(url: str) -> HttpResponse:
    response = HttpResponse(status=204)
    response["HX-Redirect"] = url
    return response
