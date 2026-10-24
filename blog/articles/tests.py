from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import (
    Article,
    Enterprise,
    ExchangeRate,
    FinancialIndicator,
    IndicatorValue,
    ReportPeriod,
)


class ArticleDetailAndArchiveTests(TestCase):
    def setUp(self):
        self.author = get_user_model().objects.create_user(
            username="analyst24", password="test-password-93"
        )
        self.article = Article.objects.create(
            title="Динамика выручки предприятия",
            author=self.author,
            text=(
                "В отчётном периоде выручка предприятия выросла. "
                "Аналитики сравнили показатели за два периода и оценили их "
                "влияние на финансовый результат холдинга."
            ),
        )

    def test_archive_lists_article_and_links_title_to_detail(self):
        response = self.client.get(reverse("archive"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.title)
        self.assertContains(response, "analyst24")
        self.assertContains(response, reverse("get_article", args=[self.article.id]))

    def test_article_detail_displays_full_article_and_back_link(self):
        response = self.client.get(reverse("get_article", args=[self.article.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.title)
        self.assertContains(response, self.article.text)
        self.assertContains(response, "Все записи")
        self.assertContains(response, "analyst24")

    def test_unknown_article_returns_404(self):
        response = self.client.get(reverse("get_article", args=[999999]))
        self.assertEqual(response.status_code, 404)

    def test_non_numeric_article_id_does_not_match_detail_route(self):
        response = self.client.get("/article/not-a-number/")
        self.assertEqual(response.status_code, 404)

    def test_excerpt_is_limited_to_140_characters_plus_ellipsis(self):
        self.article.text = "x" * 150
        self.assertEqual(self.article.get_excerpt(), "x" * 140 + "...")
        self.article.text = "short text"
        self.assertEqual(self.article.get_excerpt(), "short text")


class FinancialDashboardTests(TestCase):
    def test_financial_dashboard_renders_enterprises_indicators_and_rates(self):
        enterprise = Enterprise.objects.create(
            name="Учебное предприятие Альфа",
            requisites="DEMO-001",
            phone="+7 000 000-00-01",
            contact_person="Иван Иванов",
        )
        period = ReportPeriod.objects.create(
            title="I квартал 2026",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 3, 31),
        )
        indicator = FinancialIndicator.objects.create(
            name="Выручка",
            importance=Decimal("1.000"),
            unit="money",
            currency="RUB",
        )
        IndicatorValue.objects.create(
            enterprise=enterprise,
            report_period=period,
            indicator=indicator,
            value=Decimal("1500000.00"),
        )
        ExchangeRate.objects.create(
            base_currency="USD",
            quote_currency="RUB",
            rate=Decimal("90.000000"),
            effective_date=date(2026, 3, 31),
        )
        response = self.client.get(reverse("financial-dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Учебное предприятие Альфа")
        self.assertContains(response, "1500000")
        self.assertContains(response, "USD")



class CreatePostTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="financial_writer", password="test-password-93"
        )
        self.existing_article = Article.objects.create(
            title="Уникальный отчёт о выручке",
            author=self.user,
            text="Текст ранее опубликованной аналитической статьи.",
        )

    def test_anonymous_user_cannot_open_create_form(self):
        response = self.client.get(reverse("create_post"))
        self.assertEqual(response.status_code, 404)

    def test_authenticated_user_can_open_form(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("create_post"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_post.html")
        self.assertContains(response, "Сохранить статью")
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_valid_post_creates_article_for_current_user_and_redirects(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("create_post"),
            {"title": "Прибыль за второй квартал", "text": "Прибыль увеличилась."},
        )
        article = Article.objects.get(title="Прибыль за второй квартал")
        self.assertEqual(article.author, self.user)
        self.assertEqual(article.text, "Прибыль увеличилась.")
        self.assertRedirects(response, reverse("get_article", args=[article.id]))

    def test_empty_fields_return_form_with_error_and_preserve_input(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("create_post"),
            {"title": "Черновик без текста", "text": "   "},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Заполните название и текст статьи.")
        self.assertContains(response, "Черновик без текста")
        self.assertEqual(Article.objects.count(), 1)

    def test_duplicate_title_is_rejected_case_insensitively(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("create_post"),
            {"title": "уникальный отчёт о ВЫРУЧКЕ", "text": "Другой текст."},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Статья с таким названием уже существует")
        self.assertEqual(Article.objects.count(), 1)


class RegistrationAndLoginTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.existing_user = self.User.objects.create_user(
            username="ExistingAnalyst",
            email="existing@example.com",
            password="Existing-Password-2026!",
        )

    def test_archive_and_article_pages_show_register_link_for_anonymous_users(self):
        article = Article.objects.create(
            title="Регистрация в финансовом блоге",
            author=self.existing_user,
            text="Проверка ссылки регистрации на страницах.",
        )
        archive = self.client.get(reverse("archive"))
        detail = self.client.get(reverse("get_article", args=[article.id]))
        self.assertContains(archive, reverse("register"))
        self.assertContains(detail, reverse("register"))
        self.assertContains(archive, reverse("login"))
        self.assertContains(detail, reverse("login"))

    def test_registration_page_loads(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Регистрация пользователя")
        self.assertContains(response, 'name="password_confirm"')

    def test_registration_creates_user_hashes_password_and_logs_them_in(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "new_analyst24",
                "email": "new.analyst@example.com",
                "password": "Safe-Finance-Password-2026!",
                "password_confirm": "Safe-Finance-Password-2026!",
            },
        )
        self.assertRedirects(response, reverse("archive"))
        created = self.User.objects.get(username="new_analyst24")
        self.assertEqual(created.email, "new.analyst@example.com")
        self.assertTrue(created.check_password("Safe-Finance-Password-2026!"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_registration_rejects_casefolded_duplicate_username(self):
        self.User.objects.create_user(
            username="Аналитик24", password="Existing-Password-2026!"
        )
        response = self.client.post(
            reverse("register"),
            {
                "username": "аналитик24",
                "email": "another@example.com",
                "password": "Safe-Finance-Password-2026!",
                "password_confirm": "Safe-Finance-Password-2026!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Пользователь с таким логином уже существует")
        self.assertFalse(self.User.objects.filter(username="аналитик24").exists())

    def test_registration_rejects_empty_fields(self):
        response = self.client.post(
            reverse("register"),
            {"username": "", "email": "", "password": "", "password_confirm": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Заполните все поля формы")
        self.assertEqual(self.User.objects.count(), 1)

    def test_registration_rejects_mismatched_passwords(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "new_analyst24",
                "email": "new.analyst@example.com",
                "password": "Safe-Finance-Password-2026!",
                "password_confirm": "Different-Password-2026!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Пароли не совпадают")
        self.assertFalse(self.User.objects.filter(username="new_analyst24").exists())

    def test_registration_rejects_invalid_email_and_weak_password(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "new_analyst24",
                "email": "not-an-email",
                "password": "12345678",
                "password_confirm": "12345678",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "корректный адрес")
        self.assertFalse(self.User.objects.filter(username="new_analyst24").exists())

    def test_login_page_loads(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Вход в систему")

    def test_login_accepts_valid_credentials(self):
        response = self.client.post(
            reverse("login"),
            {"username": "ExistingAnalyst", "password": "Existing-Password-2026!"},
        )
        self.assertRedirects(response, reverse("archive"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_rejects_invalid_credentials(self):
        response = self.client.post(
            reverse("login"),
            {"username": "ExistingAnalyst", "password": "wrong-password"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Аккаунт с таким логином и паролем не существует")
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_rejects_empty_fields(self):
        response = self.client.post(
            reverse("login"),
            {"username": "", "password": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Введите логин и пароль")

    def test_logout_ends_session(self):
        self.client.force_login(self.existing_user)
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("archive"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_authenticated_user_is_redirected_away_from_registration_and_login(self):
        self.client.force_login(self.existing_user)
        for url_name in ("register", "login"):
            response = self.client.get(reverse(url_name))
            self.assertRedirects(response, reverse("archive"))


class JavaScriptLabTests(TestCase):
    def setUp(self):
        self.author = get_user_model().objects.create_user(
            username="js_author", password="test-password-93"
        )
        Article.objects.create(
            title="Проверка сворачивания",
            author=self.author,
            text="Текст статьи для проверки DOM.",
        )

    def test_archive_loads_both_javascript_files(self):
        response = self.client.get(reverse("archive"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "js/helloworld.js")
        self.assertContains(response, "js/fold-post.js")

    def test_each_archive_article_has_fold_button_and_student_filters(self):
        response = self.client.get(reverse("archive"))
        self.assertContains(response, 'class="fold-button"')
        self.assertContains(response, 'id="group-filter-input"')
        self.assertContains(response, 'id="average-filter-input"')
        self.assertContains(response, 'id="student-results"')
