from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Article(models.Model):
    """Analyst note, following the model described in the lab handout."""
    title = models.CharField("Заголовок", max_length=200, unique=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Автор",
        related_name="financial_articles",
    )
    text = models.TextField("Текст")
    created_date = models.DateField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Статья аналитика"
        verbose_name_plural = "Статьи аналитиков"
        ordering = ("-created_date", "-id")

    def __str__(self):
        return f"{self.author.username}: {self.title}"

    def get_excerpt(self):
        return self.text[:140] + "..." if len(self.text) > 140 else self.text


class Enterprise(models.Model):
    """Enterprise included in the holding company, as specified by variant 24."""
    name = models.CharField("Название предприятия", max_length=200, unique=True)
    requisites = models.CharField("Реквизиты", max_length=255)
    phone = models.CharField("Телефон", max_length=50)
    contact_person = models.CharField("Контактное лицо", max_length=150)

    class Meta:
        verbose_name = "Предприятие"
        verbose_name_plural = "Предприятия"
        ordering = ("name",)

    def __str__(self):
        return self.name


class ReportPeriod(models.Model):
    title = models.CharField("Отчётный период", max_length=100, unique=True)
    start_date = models.DateField("Начало периода")
    end_date = models.DateField("Окончание периода")

    class Meta:
        verbose_name = "Отчётный период"
        verbose_name_plural = "Отчётные периоды"
        ordering = ("-start_date",)

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError({"end_date": "Окончание периода не может быть раньше его начала."})

    def __str__(self):
        return self.title


class FinancialIndicator(models.Model):
    CURRENCY_CHOICES = [
        ("RUB", "Российский рубль (RUB)"),
        ("USD", "Доллар США (USD)"),
        ("EUR", "Евро (EUR)"),
    ]
    UNIT_CHOICES = [
        ("money", "Денежная величина"),
        ("percent", "Процент"),
        ("count", "Количество"),
        ("other", "Другая единица"),
    ]

    name = models.CharField("Название показателя", max_length=150, unique=True)
    importance = models.DecimalField("Коэффициент важности", max_digits=8, decimal_places=3)
    unit = models.CharField("Единица измерения", max_length=12, choices=UNIT_CHOICES, default="money")
    currency = models.CharField("Валюта", max_length=3, choices=CURRENCY_CHOICES, default="RUB")
    description = models.TextField("Описание", blank=True)

    class Meta:
        verbose_name = "Финансовый показатель"
        verbose_name_plural = "Финансовые показатели"
        ordering = ("name",)

    def __str__(self):
        return f"{self.name} ({self.currency})"


class IndicatorValue(models.Model):
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE, verbose_name="Предприятие")
    report_period = models.ForeignKey(ReportPeriod, on_delete=models.CASCADE, verbose_name="Отчётный период")
    indicator = models.ForeignKey(FinancialIndicator, on_delete=models.CASCADE, verbose_name="Показатель")
    value = models.DecimalField("Значение", max_digits=18, decimal_places=2)
    note = models.CharField("Примечание", max_length=255, blank=True)

    class Meta:
        verbose_name = "Значение показателя"
        verbose_name_plural = "Значения показателей"
        ordering = ("-report_period__start_date", "enterprise__name", "indicator__name")
        constraints = [
            models.UniqueConstraint(
                fields=("enterprise", "report_period", "indicator"),
                name="unique_enterprise_period_indicator",
            ),
        ]

    def __str__(self):
        return f"{self.enterprise} — {self.indicator}: {self.value} ({self.report_period})"


class ExchangeRate(models.Model):
    CURRENCY_CHOICES = FinancialIndicator.CURRENCY_CHOICES
    base_currency = models.CharField("Базовая валюта", max_length=3, choices=CURRENCY_CHOICES)
    quote_currency = models.CharField("Валюта котировки", max_length=3, choices=CURRENCY_CHOICES)
    rate = models.DecimalField("Курс", max_digits=18, decimal_places=6)
    effective_date = models.DateField("Дата действия курса")

    class Meta:
        verbose_name = "Курс валюты"
        verbose_name_plural = "Курсы валют"
        ordering = ("-effective_date", "base_currency", "quote_currency")
        constraints = [
            models.UniqueConstraint(
                fields=("base_currency", "quote_currency", "effective_date"),
                name="unique_currency_pair_date",
            ),
        ]

    def clean(self):
        if self.base_currency == self.quote_currency:
            raise ValidationError("Базовая валюта и валюта котировки должны различаться.")
        if self.rate <= 0:
            raise ValidationError({"rate": "Курс должен быть положительным."})

    def __str__(self):
        return f"1 {self.base_currency} = {self.rate} {self.quote_currency} ({self.effective_date})"
