from django.core.paginator import Paginator

from .constants import POSTS_PER_PAGE


def paginate(request, queryset):
    """
    Делит список объектов, переданных в queryset, на страницы.
    Количество страниц определяется автоматически из заданной константы.
    """

    paginator = Paginator(object_list=queryset, per_page=POSTS_PER_PAGE)
    return paginator.get_page(number=request.GET.get("page"))
