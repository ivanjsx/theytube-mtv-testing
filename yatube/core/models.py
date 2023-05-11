from django.db import models


class CreatedModel(models.Model):
    """Абстрактная модель. Добавляет дату и время создания объекта модели."""

    created = models.DateTimeField(
        verbose_name="Дата и время создания",
        auto_now_add=True,
        editable=False,
        db_index=True,
    )

    class Meta:
        abstract = True
