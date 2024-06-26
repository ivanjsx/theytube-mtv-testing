# Generated by Django 2.2.28 on 2023-05-07 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_auto_20230507_1600'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('-pub_date',), 'verbose_name': 'Пост', 'verbose_name_plural': 'Посты'},
        ),
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, help_text='Загрузите картинку', upload_to='posts/', verbose_name='Заглавная картинка поста'),
        ),
    ]
