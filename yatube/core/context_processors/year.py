from datetime import date


def year(request):
    """Добавляет в контекст переменную с текущим годом."""
    return {
        "year": date.today().year,
    }
