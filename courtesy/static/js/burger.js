document.addEventListener("DOMContentLoaded", function () {
    const burgerToggle = document.querySelector(".burger-toggle");
    const burgerMenu = document.querySelector(".burger-menu");
    const arrow = document.querySelector(".burger-toggle .arrow");

    burgerToggle.addEventListener("click", function (event) {
        event.preventDefault();
        burgerMenu.classList.toggle("active");
        arrow.classList.toggle("rotated");
    });
});