document.addEventListener("DOMContentLoaded", function () {
    const burgerToggle = document.querySelector(".burger-toggle");
    const burgerMenu = document.querySelector(".burger-menu");
    const arrow = document.querySelector(".burger-toggle .arrow");

    burgerToggle.addEventListener("click", function (event) {
        event.preventDefault(); // Предотвращаем переход по ссылке
        burgerMenu.classList.toggle("active"); // Переключаем класс активности меню
        arrow.classList.toggle("rotated"); // Переключаем класс для стрелки
    });
});