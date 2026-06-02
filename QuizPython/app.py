from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)
DB_NAME = 'quiz.db'

# Data dummy berbentuk array sesuai request
DUMMY_QUESTIONS = [
    {
        "text": "Apa keyword yang digunakan untuk membuat fungsi dalam bahasa Python?",
        "choices": [
            {"text": "function", "is_correct": 0},
            {"text": "def", "is_correct": 1},
            {"text": "func", "is_correct": 0},
            {"text": "define", "is_correct": 0}
        ]
    },
    {
        "text": "Manakah di bawah ini yang BUKAN merupakan tipe data bawaan (built-in) di Python?",
        "choices": [
            {"text": "list", "is_correct": 0},
            {"text": "dictionary", "is_correct": 0},
            {"text": "array", "is_correct": 1},
            {"text": "tuple", "is_correct": 0}
        ]
    },
    {
        "text": "Bagaimana cara mengambil panjang atau jumlah elemen dari sebuah list di Python?",
        "choices": [
            {"text": "list.length()", "is_correct": 0},
            {"text": "len(list)", "is_correct": 1},
            {"text": "length(list)", "is_correct": 0},
            {"text": "list.size()", "is_correct": 0}
        ]
    },
    {
        "text": "Apa output yang dihasilkan dari perintah: print(type([])) ?",
        "choices": [
            {"text": "<class 'list'>", "is_correct": 1},
            {"text": "<class 'array'>", "is_correct": 0},
            {"text": "<class 'tuple'>", "is_correct": 0},
            {"text": "<class 'dict'>", "is_correct": 0}
        ]
    }
]


# Inisialisasi database dan sinkronisasi data dummy
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Buat Tabel Pertanyaan
    c.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_text TEXT NOT NULL
        )
    ''')

    # Buat Tabel Pilihan Jawaban
    c.execute('''
        CREATE TABLE IF NOT EXISTS choices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER,
            choice_text TEXT NOT NULL,
            is_correct INTEGER NOT NULL,
            FOREIGN KEY (question_id) REFERENCES questions (id)
        )
    ''')

    # Masukkan data dummy jika database masih kosong
    c.execute('SELECT COUNT(*) FROM questions')
    if c.fetchone()[0] == 0:
        for q in DUMMY_QUESTIONS:
            c.execute('INSERT INTO questions (question_text) VALUES (?)', (q['text'],))
            q_id = c.lastrowid
            for choice in q['choices']:
                c.execute('INSERT INTO choices (question_id, choice_text, is_correct) VALUES (?, ?, ?)',
                          (q_id, choice['text'], choice['is_correct']))
        conn.commit()
    conn.close()


# Mengambil data kuis dari SQLite
def get_quiz_data():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM questions')
    questions = [dict(row) for row in c.fetchall()]

    for q in questions:
        c.execute('SELECT * FROM choices WHERE question_id = ?', (q['id'],))
        q['choices'] = [dict(row) for row in c.fetchall()]

    conn.close()
    return questions


# Route Utama untuk Menampilkan Kuis & Memproses Jawaban
@app.route('/', methods=['GET', 'POST'])
def index():
    questions = get_quiz_data()
    score = None
    total = len(questions)
    user_answers = {}
    submitted = False

    if request.method == 'POST':
        submitted = True
        score = 0
        for q in questions:
            field_name = f"question_{q['id']}"
            selected_choice_id = request.form.get(field_name)

            # Simpan jawaban user untuk tracking di UI
            user_answers[q['id']] = int(selected_choice_id) if selected_choice_id else None

            # Validasi skor berdasarkan database
            if selected_choice_id:
                for choice in q['choices']:
                    if choice['id'] == int(selected_choice_id) and choice['is_correct'] == 1:
                        score += 1

    return render_template('index.html', questions=questions, score=score, total=total, user_answers=user_answers,
                           submitted=submitted)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)