document.addEventListener("DOMContentLoaded", function() {
    const imageBox = document.getElementById("imageBox");
    const featuresContent = document.querySelector(".features-content");

    function checkVisibility() {
        const rect = imageBox.getBoundingClientRect();
        if (rect.top <= window.innerHeight && rect.bottom >= 0) {
            imageBox.style.opacity = "1";
            featuresContent.style.opacity = "1";
        }
    }

    // Check visibility on page load
    checkVisibility();

    // Check visibility on scroll
    window.addEventListener("scroll", checkVisibility);
});
