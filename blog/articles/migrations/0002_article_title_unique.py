from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("articles", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="article",
            name="title",
            field=models.CharField(max_length=200, unique=True, verbose_name="Заголовок"),
        ),
    ]
