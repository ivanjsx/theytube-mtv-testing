from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    """Добавляет тегу, к которому применяется, указанный в параметре класс"""

    return field.as_widget(attrs={"class": css})


@register.filter
def count_items(queryset):
    return queryset.count()


@register.filter
def uglify(text: str) -> str:
    """иЗмЕнЯеТ РеГиСтР БуКв нА ВоТ ТаКоЙ"""

    return "".join(
        [
            char.upper() if i % 2
            else char.lower()
            for i, char in enumerate(text)
        ]
    )
