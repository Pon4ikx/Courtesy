document.addEventListener("DOMContentLoaded", function () {
    const scrollToTopBtn = document.getElementById("scrollToTopBtn");

    // Показать/спрятать кнопку с анимацией
    window.addEventListener("scroll", function () {
        if (window.pageYOffset > 300) {
            scrollToTopBtn.classList.add("show");
        } else {
            scrollToTopBtn.classList.remove("show");
        }
    });

    // Плавная прокрутка наверх
    scrollToTopBtn.addEventListener("click", function () {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
});
