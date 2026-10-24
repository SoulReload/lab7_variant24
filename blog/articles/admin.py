from django.contrib import admin
from .models import Article, Enterprise, ExchangeRate, FinancialIndicator, IndicatorValue, ReportPeriod


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "get_excerpt", "created_date")
    list_filter = ("created_date", "author")
    search_fields = ("title", "text", "author__username")
    readonly_fields = ("created_date",)


@admin.register(Enterprise)
class EnterpriseAdmin(admin.ModelAdmin):
    list_display = ("name", "requisites", "phone", "contact_person")
    search_fields = ("name", "requisites", "contact_person")


@admin.register(ReportPeriod)
class ReportPeriodAdmin(admin.ModelAdmin):
    list_display = ("title", "start_date", "end_date")
    list_filter = ("start_date",)
    search_fields = ("title",)


@admin.register(FinancialIndicator)
class FinancialIndicatorAdmin(admin.ModelAdmin):
    list_display = ("name", "importance", "unit", "currency")
    list_filter = ("unit", "currency")
    search_fields = ("name", "description")


@admin.register(IndicatorValue)
class IndicatorValueAdmin(admin.ModelAdmin):
    list_display = ("enterprise", "report_period", "indicator", "value")
    list_filter = ("report_period", "indicator__currency", "enterprise")
    search_fields = ("enterprise__name", "indicator__name", "report_period__title")


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ("base_currency", "quote_currency", "rate", "effective_date")
    list_filter = ("base_currency", "quote_currency", "effective_date")
