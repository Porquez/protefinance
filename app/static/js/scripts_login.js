document.addEventListener("DOMContentLoaded", function () {
  const loginForm = document.getElementById("loginForm");
  const loginMessage = document.getElementById("loginMessage");
  const togglePasswordButton = document.getElementById("togglePassword");
  const csrfTokenElement = document.querySelector('input[name="csrf_token"]');

  // Log the CSRF token value
  console.log("CSRF Token:", csrfTokenElement.value);

  loginForm.addEventListener("submit", function (event) {
    event.preventDefault();
    loginMessage.innerText = "Connexion en cours...";

    let formData = {
      username: loginForm.username.value,
      password: loginForm.password.value,
    };

    // Log the form data
    console.log("Submitting login form with data:", formData);

    fetch("/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfTokenElement.value, // Ajouter le CSRF token
      },
      body: JSON.stringify(formData),
    })
    .then((response) => {
      // Log the response status
      console.log("Response Status:", response.status);

      if (!response.ok) {
        return response.json().then(data => {
          loginMessage.innerText = data.error || "Erreur de connexion. Veuillez réessayer.";
          // Log the error response
          console.error("Error response data:", data);
        });
      } else {
        window.location.href = "/";
      }
    })
    .catch((error) => {
      loginMessage.innerText = "Erreur de connexion. Veuillez réessayer.";
      console.error("Fetch Error:", error);
    });
  });

  togglePasswordButton.addEventListener("click", function () {
    const passwordField = document.getElementById("password");
    const passwordFieldType = passwordField.getAttribute("type");
    if (passwordFieldType === "password") {
      passwordField.setAttribute("type", "text");
      this.textContent = "Cacher";
    } else {
      passwordField.setAttribute("type", "password");
      this.textContent = "Afficher";
    }
  });
});
