document.addEventListener("DOMContentLoaded", function () {
    const doctorSelect = document.querySelector("#id_doctor");
    const serviceField = document.querySelector("#id_service");

    if (doctorSelect && serviceField) {
        doctorSelect.addEventListener("change", function () {
            const doctorId = doctorSelect.value;
            const url = new URL(window.location.href);
            url.searchParams.set("doctor", doctorId);
            window.location.href = url.toString();
        });
    }
});
