export function saveToLocalStorage(key, data) {
    if (!key || !data) {
        console.error('Ключ или данные отсутствуют');
        return;
    }
    try {
        localStorage.setItem(key, JSON.stringify(data));
    } catch (error) {
        console.error('Ошибка при сохранении данных:', error);
    }
}

export function getFromLocalStorage(key) {
    if (!key) {
        console.error('Ключ отсутствует');
        return null;
    }
    const data = localStorage.getItem(key);
    if (!data) return null;

    try {
        return JSON.parse(data);
    } catch (error) {
        console.error('Ошибка при парсинге JSON:', error);
        return null;
    }
}

export function redirectTo(url) {
    window.location.href = url;
}