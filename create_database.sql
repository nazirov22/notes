DROP TABLE IF EXISTS Note_Tag;

DROP TABLE IF EXISTS Tag;

DROP TABLE IF EXISTS Note;

DROP TABLE IF EXISTS Category;

DROP TABLE IF EXISTS User;

CREATE TABLE
    User (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    );

CREATE TABLE
    Category (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    );

CREATE TABLE
    Note (
        note_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        creation_date DATETIME NOT NULL,
        last_modified DATETIME NOT NULL,
        is_archived BOOLEAN NOT NULL DEFAULT 0,
        user_id INTEGER NOT NULL,
        category_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES User (user_id) ON DELETE CASCADE,
        FOREIGN KEY (category_id) REFERENCES Category (category_id) ON DELETE RESTRICT
    );

CREATE TABLE
    Tag (
        tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    );

CREATE TABLE
    Note_Tag (
        note_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        PRIMARY KEY (note_id, tag_id),
        FOREIGN KEY (note_id) REFERENCES Note (note_id) ON DELETE CASCADE,
        FOREIGN KEY (tag_id) REFERENCES Tag (tag_id) ON DELETE CASCADE
    );

-- Вставка начальных данных для тестирования
INSERT INTO
    User (username, email, password)
VALUES
    ('user1', 'user1@example.com', 'hashed_password_1'),
    ('user2', 'user2@example.com', 'hashed_password_2');

INSERT INTO
    User (username, email, password)
VALUES
    ('testuser', 'test@example.com', 'testpass');

INSERT INTO
    Category (name)
VALUES
    ('Работа'),
    ('Учёба'),
    ('Личное');

INSERT INTO
    Tag (name)
VALUES
    ('Важно'),
    ('Срочно');