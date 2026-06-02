CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_text TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS choices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER,
            choice_text TEXT NOT NULL,
            is_correct INTEGER NOT NULL,
            FOREIGN KEY (question_id) REFERENCES questions (id)
        );
