import { redirectTo } from './utils.js';
import { getCookie } from './utils.js';

export async function displayNotes(filter = '', category_id = null) {
    const notesContainer = document.getElementById('notesContainer');
    if (!notesContainer) {
        console.error('Контейнер для заметок не найден');
        return;
    }
    notesContainer.innerHTML = '';

    const user_id = getCookie('user_id');
    if (!user_id) {
        alert('Пожалуйста, войдите в систему');
        redirectTo('login.html');
        return;
    }

    // let url = `http://localhost:5000/notes?user_id=${user_id}`;
    let url = `/notes?user_id=${user_id}`;


    if (filter) url += `&search_query=${encodeURIComponent(filter)}`;
    if (category_id) url += `&category_id=${category_id}`;

    const response = await fetch(url);
    const notes = await response.json();

    notes.forEach(note => {
        const noteElement = document.createElement('div');
        noteElement.className = 'note';
        noteElement.innerHTML = `
            <h3>${note.title}</h3>
            <p>${note.content}</p>
            <span class="date">${new Date(note.creation_date).toLocaleDateString()}</span>
            <p>Категория: ${note.category}</p>
            <div class="actions">
                <button onclick="editNote(${note.note_id})">Редактировать</button>
                <button onclick="deleteNote(${note.note_id})">Удалить</button>
            </div>
        `;
        notesContainer.appendChild(noteElement);
    });
}

export function editNote(id) {
    redirectTo(`edit-note.html?id=${id}`);
}

export async function deleteNote(id) {
    if (confirm('Вы уверены, что хотите удалить эту заметку?')) {
        const user_id = getCookie('user_id');
        // await fetch(`http://localhost:5000/notes/${id}`, {
        await fetch(`/notes/${id}`, {

            method: 'DELETE',
            headers: { 'user-id': user_id }
        });
        displayNotes();
    }
}

document.addEventListener('DOMContentLoaded', async function () {
    const searchInput = document.getElementById('searchInput');
    const categoriesContainer = document.getElementById('categories');

    // const response = await fetch('http://localhost:5000/categories');
    const response = await fetch('/categories');


    const categories = await response.json();
    categoriesContainer.innerHTML = '';
    categories.forEach(cat => {
        const li = document.createElement('li');
        li.textContent = cat.name;
        li.setAttribute('data-category', cat.category_id);
        categoriesContainer.appendChild(li);
    });

    let currentCategory = null;

    searchInput.addEventListener('input', function () {
        displayNotes(this.value, currentCategory);
    });

    categoriesContainer.addEventListener('click', function (e) {
        if (e.target.tagName === 'LI') {
            const selectedCategory = e.target.getAttribute('data-category');
            if (currentCategory === selectedCategory) {
                currentCategory = null;
                e.target.classList.remove('active');
            } else {
                categoriesContainer.querySelectorAll('li').forEach(c => c.classList.remove('active'));
                e.target.classList.add('active');
                currentCategory = selectedCategory;
            }
            displayNotes(searchInput.value, currentCategory);
        }
    });
});