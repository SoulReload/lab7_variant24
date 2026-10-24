# Initial schema for the article archive and financial variant 24.
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Article",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200, verbose_name="Заголовок")),
                ("text", models.TextField(verbose_name="Текст")),
                ("created_date", models.DateField(auto_now_add=True, verbose_name="Дата создания")),
                ("author", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="financial_articles", to=settings.AUTH_USER_MODEL, verbose_name="Автор")),
            ],
            options={"verbose_name": "Статья аналитика", "verbose_name_plural": "Статьи аналитиков", "ordering": ("-created_date", "-id")},
        ),
        migrations.CreateModel(
            name="Enterprise",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200, unique=True, verbose_name="Название предприятия")),
                ("requisites", models.CharField(max_length=255, verbose_name="Реквизиты")),
                ("phone", models.CharField(max_length=50, verbose_name="Телефон")),
                ("contact_person", models.CharField(max_length=150, verbose_name="Контактное лицо")),
            ],
            options={"verbose_name": "Предприятие", "verbose_name_plural": "Предприятия", "ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="ReportPeriod",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=100, unique=True, verbose_name="Отчётный период")),
                ("start_date", models.DateField(verbose_name="Начало периода")),
                ("end_date", models.DateField(verbose_name="Окончание периода")),
            ],
            options={"verbose_name": "Отчётный период", "verbose_name_plural": "Отчётные периоды", "ordering": ("-start_date",)},
        ),
        migrations.CreateModel(
            name="FinancialIndicator",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150, unique=True, verbose_name="Название показателя")),
                ("importance", models.DecimalField(decimal_places=3, max_digits=8, verbose_name="Коэффициент важности")),
                ("unit", models.CharField(choices=[("money", "Денежная величина"), ("percent", "Процент"), ("count", "Количество"), ("other", "Другая единица")], default="money", max_length=12, verbose_name="Единица измерения")),
                ("currency", models.CharField(choices=[("RUB", "Российский рубль (RUB)"), ("USD", "Доллар США (USD)"), ("EUR", "Евро (EUR)")], default="RUB", max_length=3, verbose_name="Валюта")),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
            ],
            options={"verbose_name": "Финансовый показатель", "verbose_name_plural": "Финансовые показатели", "ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="IndicatorValue",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("value", models.DecimalField(decimal_places=2, max_digits=18, verbose_name="Значение")),
                ("note", models.CharField(blank=True, max_length=255, verbose_name="Примечание")),
                ("enterprise", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="articles.enterprise", verbose_name="Предприятие")),
                ("indicator", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="articles.financialindicator", verbose_name="Показатель")),
                ("report_period", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="articles.reportperiod", verbose_name="Отчётный период")),
            ],
            options={"verbose_name": "Значение показателя", "verbose_name_plural": "Значения показателей", "ordering": ("-report_period__start_date", "enterprise__name", "indicator__name")},
        ),
        migrations.CreateModel(
            name="ExchangeRate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("base_currency", models.CharField(choices=[("RUB", "Российский рубль (RUB)"), ("USD", "Доллар США (USD)"), ("EUR", "Евро (EUR)")], max_length=3, verbose_name="Базовая валюта")),
                ("quote_currency", models.CharField(choices=[("RUB", "Российский рубль (RUB)"), ("USD", "Доллар США (USD)"), ("EUR", "Евро (EUR)")], max_length=3, verbose_name="Валюта котировки")),
                ("rate", models.DecimalField(decimal_places=6, max_digits=18, verbose_name="Курс")),
                ("effective_date", models.DateField(verbose_name="Дата действия курса")),
            ],
            options={"verbose_name": "Курс валюты", "verbose_name_plural": "Курсы валют", "ordering": ("-effective_date", "base_currency", "quote_currency")},
        ),
        migrations.AddConstraint(
            model_name="indicatorvalue",
            constraint=models.UniqueConstraint(fields=("enterprise", "report_period", "indicator"), name="unique_enterprise_period_indicator"),
        ),
        migrations.AddConstraint(
            model_name="exchangerate",
            constraint=models.UniqueConstraint(fields=("base_currency", "quote_currency", "effective_date"), name="unique_currency_pair_date"),
        ),
    ]
