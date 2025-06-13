export function saveToLocalStorage(key, data) {
    console.warn('saveToLocalStorage is disabled. Use server storage instead.');
}

export function getFromLocalStorage(key) {
    console.warn('getFromLocalStorage is disabled. Use server storage instead.');
    return null;
}

export function redirectTo(url) {
    window.location.href = url;
}

export function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}