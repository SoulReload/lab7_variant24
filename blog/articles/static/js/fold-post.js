"use strict";

// Delegated обработчик работает даже если карточки появились после загрузки страницы.
// Класс folded добавляется именно карточке .one-post, а не кнопке.
document.addEventListener("click", function (event) {
    var target = event.target;
    if (!target || typeof target.closest !== "function") {
        return;
    }

    var button = target.closest(".fold-button");
    if (!button) {
        return;
    }

    var post = button.closest(".one-post");
    if (!post) {
        console.error("Кнопка сворачивания должна находиться внутри .one-post");
        return;
    }

    var isFolded = !post.classList.contains("folded");
    post.classList.toggle("folded", isFolded);
    button.textContent = isFolded ? "развернуть" : "свернуть";
    button.setAttribute("aria-expanded", isFolded ? "false" : "true");

    console.log("Состояние статьи:", isFolded ? "свернута" : "развернута", post);
});
