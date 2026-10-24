"use strict";

// Компактное управление видимостью карточки через CSS-класс родителя.
var foldBtns = document.getElementsByClassName("fold-button");
for (var i = 0; i < foldBtns.length; i++) {
    foldBtns[i].addEventListener("click", function (event) {
        var button = event.currentTarget;
        var post = button.closest(".one-post");
        if (!post) {
            return;
        }

        var isFolded = post.classList.toggle("folded");
        button.textContent = isFolded ? "развернуть" : "свернуть";
        button.setAttribute("aria-expanded", String(!isFolded));
        console.log("you clicked ", event.target);
    });
}
