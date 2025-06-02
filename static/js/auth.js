import { redirectTo } from './utils.js';

export async function registerUser(username, email, password) {
    if (!username || !email || !password) {
        alert('Пожалуйста, заполните все поля');
        return;
    }

    const response = await fetch('http://localhost:5000/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password })
    });
    const result = await response.json();
    if (response.ok) {
        alert(result.message);
        redirectTo('login.html');
    } else {
        alert(result.error);
    }
}

export async function loginUser(username, password) {
    if (!username || !password) {
        alert('Пожалуйста, заполните все поля');
        return;
    }

    const response = await fetch('http://localhost:5000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    const result = await response.json();
    if (response.ok) {
        alert(result.message);
        localStorage.setItem('user_id', result.user_id);
        redirectTo('notes.html');
    } else {
        alert(result.error);
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const registerForm = document.querySelector('form');
    if (registerForm && window.location.pathname.includes('register.html')) {
        registerForm.addEventListener('submit', async function (event) {
            event.preventDefault();
            const username = registerForm.querySelector('input[type="text"]').value;
            const email = registerForm.querySelector('input[type="email"]').value;
            const password = registerForm.querySelector('input[type="password"]').value;
            await registerUser(username, email, password);
        });
    }

    const loginForm = document.querySelector('form');
    if (loginForm && window.location.pathname.includes('login.html')) {
        loginForm.addEventListener('submit', async function (event) {
            event.preventDefault();
            const username = loginForm.querySelector('input[type="text"]').value;
            const password = loginForm.querySelector('input[type="password"]').value;
            await loginUser(username, password);
        });
    }
});