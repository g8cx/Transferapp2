// This file contains JavaScript functionality specific to the authentication pages, such as form validation or handling user interactions.

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('form');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            // Perform any necessary validation before submitting the form
            const username = document.querySelector('#id_username').value;
            const password = document.querySelector('#id_password').value;

            if (!username || !password) {
                event.preventDefault();
                alert('Please fill in both username and password.');
            }
        });
    }

    const registerForm = document.querySelector('form');
    
    if (registerForm) {
        registerForm.addEventListener('submit', function(event) {
            // Perform any necessary validation before submitting the form
            const email = document.querySelector('#id_email').value;
            const username = document.querySelector('#id_username').value;
            const password = document.querySelector('#id_password').value;

            if (!email || !username || !password) {
                event.preventDefault();
                alert('Please fill in all fields.');
            }
        });
    }
});