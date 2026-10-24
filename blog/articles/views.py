from django.contrib.auth import authenticate, get_user_model, login as auth_login, logout as auth_logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import Http404, HttpResponseNotAllowed
from django.shortcuts import redirect, render

from .models import Article, Enterprise, ExchangeRate, IndicatorValue


def archive(request):
    """Show all analyst articles; each title links to its detail page."""
    posts = Article.objects.select_related("author").order_by("-created_date", "-id")
    return render(request, "archive.html", {"posts": posts})


def get_article(request, article_id):
    """Show a single article selected by its numeric database ID."""
    try:
        post = Article.objects.select_related("author").get(id=article_id)
    except Article.DoesNotExist as exc:
        raise Http404("Статья не найдена") from exc
    return render(request, "article.html", {"post": post})


def financial_dashboard(request):
    """Overview of financial indicators and exchange rates for variant 24."""
    enterprises = Enterprise.objects.all()
    values = IndicatorValue.objects.select_related(
        "enterprise", "report_period", "indicator"
    ).order_by("-report_period__start_date", "enterprise__name", "indicator__name")
    rates = ExchangeRate.objects.all().order_by("-effective_date")[:30]
    return render(
        request,
        "financial_dashboard.html",
        {"enterprises": enterprises, "indicator_values": values, "exchange_rates": rates},
    )


def create_post(request):
    """Create an article for the authenticated user."""
    if not request.user.is_authenticated:
        raise Http404

    initial_form = {"title": "", "text": ""}
    if request.method != "POST":
        return render(request, "create_post.html", {"form": initial_form})

    title = request.POST.get("title", "").strip()
    text = request.POST.get("text", "").strip()
    form = {"title": title, "text": text}

    if not title or not text:
        form["errors"] = "Заполните название и текст статьи."
        return render(request, "create_post.html", {"form": form})

    # SQLite's built-in case-insensitive comparison does not reliably handle
    # Cyrillic characters. Compare casefolded titles in Python instead.
    normalized_title = title.casefold()
    existing_titles = Article.objects.values_list("title", flat=True)
    title_exists = any(
        existing_title.casefold() == normalized_title
        for existing_title in existing_titles
    )
    if title_exists:
        form["errors"] = (
            "Статья с таким названием уже существует. Выберите другое название."
        )
        return render(request, "create_post.html", {"form": form})

    post = Article.objects.create(
        title=title,
        text=text,
        author=request.user,
    )
    return redirect("get_article", article_id=post.id)



def register_user(request):
    """Register a new user after validating the submitted form."""
    User = get_user_model()
    if request.user.is_authenticated:
        return redirect("archive")

    form = {"username": "", "email": ""}
    errors = []

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        password_confirm = request.POST.get("password_confirm", "")
        form = {"username": username, "email": email}

        if not username or not email or not password or not password_confirm:
            errors.append("Заполните все поля формы.")

        if username:
            try:
                User._meta.get_field("username").clean(username, None)
            except ValidationError as exc:
                errors.extend(exc.messages)

            # SQLite's default case-insensitive comparisons are not full Unicode.
            normalized_username = username.casefold()
            existing_usernames = User.objects.values_list("username", flat=True)
            if any(name.casefold() == normalized_username for name in existing_usernames):
                errors.append("Пользователь с таким логином уже существует.")

        if email:
            try:
                validate_email(email)
            except ValidationError:
                errors.append("Введите корректный адрес электронной почты.")

        if password and password_confirm and password != password_confirm:
            errors.append("Пароли не совпадают.")

        if password:
            candidate = User(username=username, email=email)
            try:
                validate_password(password, user=candidate)
            except ValidationError as exc:
                errors.extend(exc.messages)

        if not errors:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            auth_login(request, user)
            return redirect("archive")

        return render(request, "register.html", {"form": form, "errors": errors})

    return render(request, "register.html", {"form": form, "errors": errors})


def login_user(request):
    """Authenticate an existing user and start a Django session."""
    if request.user.is_authenticated:
        return redirect("archive")

    form = {"username": ""}
    errors = []

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        form = {"username": username}

        if not username or not password:
            errors.append("Введите логин и пароль.")
        else:
            user = authenticate(request, username=username, password=password)
            if user is None:
                errors.append("Аккаунт с таким логином и паролем не существует. Проверьте введённые данные.")
            else:
                auth_login(request, user)
                return redirect("archive")

    return render(request, "login.html", {"form": form, "errors": errors})


def logout_user(request):
    """End the current session through a CSRF-protected POST request."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    auth_logout(request)
    return redirect("archive")
