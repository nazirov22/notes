import { redirectTo } from './utils.js';
import { getCookie } from './utils.js';

document.addEventListener('DOMContentLoaded', async function () {
    const form = document.getElementById('noteForm');
    const noteTitle = document.getElementById('noteTitle');
    const noteText = document.getElementById('noteText');
    const noteCategory = document.getElementById('noteCategory');
    const deleteBtn = document.getElementById('deleteBtn');

    // Загрузка категорий
    // const categoriesResponse = await fetch('http://localhost:5000/categories');
    const categoriesResponse = await fetch('/categories');


    const categories = await categoriesResponse.json();
    noteCategory.innerHTML = categories.map(cat => `<option value="${cat.category_id}">${cat.name}</option>`).join('');

    // Загрузка тегов
    // const tagsResponse = await fetch('http://localhost:5000/tags');
    const tagsResponse = await fetch('/tags');

    const tags = await tagsResponse.json();

    const noteId = new URLSearchParams(window.location.search).get('id');
    let note = null;
    if (noteId) {
        const user_id = getCookie('user_id');
        // const response = await fetch(`http://localhost:5000/notes?user_id=${user_id}`);
        const response = await fetch(`/notes?user_id=${user_id}`);

        const notes = await response.json();
        note = notes.find(n => n.note_id == noteId);
        if (note) {
            noteTitle.value = note.title;
            noteText.value = note.content;
            noteCategory.value = note.category_id;
        }
    }

    form.onsubmit = async function (e) {
        e.preventDefault();
        const user_id = getCookie('user_id');
        const data = {
            title: noteTitle.value,
            content: noteText.value,
            category_id: noteCategory.value,
            tags: [1],
            user_id
        };

        if (note) {
            // await fetch(`http://localhost:5000/notes/${noteId}`, {
            await fetch(`/notes/${noteId}`, {

                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        } else {
            // await fetch('http://localhost:5000/notes', {
            await fetch('/notes', {

                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        }
        redirectTo('notes.html');
    };

    deleteBtn.onclick = async function () {
        if (note && confirm('Вы уверены, что хотите удалить эту заметку?')) {
            // await fetch(`http://localhost:5000/notes/${noteId}`, { method: 'DELETE' });
            await fetch(`/notes/${noteId}`, { method: 'DELETE' });

            redirectTo('notes.html');
        }
    };
});