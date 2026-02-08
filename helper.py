import json
from pathlib import Path
from datetime import datetime
import random

SCORES_FILE = Path('scores.json')

MOTIVATION = [
    "Отлично! 🔥 Ты уже на правильном пути — продолжай в том же духе!",
    "Хороший результат! 💪 Ещё немного — и ты будешь на уровне Middle!",
    "Не сдавайся! Каждый тест делает тебя сильнее 🌟",
    "Круто! Ты уже лучше, чем вчера. Горжусь тобой! 🚀",
    "Средний уровень — это нормально. Главное — расти дальше! 📈",
    "Молодец! Продолжай учиться — успех близко! 🏆"
]

QUESTIONS = {
    'Python': {
        'Легкий': [
            {'q': 'Что выведет print(2 + 2)?',
            'options': ['3', '4', '5', '6'],
            'correct': 1},

            {'q': 'Как создать пустой список?',
            'options': ['list()', '[]', '{}', '()'],
            'correct': 1},

            {'q': 'Какой тип данных для текста?',
            'options': ['int', 'str', 'float', 'bool'],
            'correct': 1},

            {'q': 'Что делает len()?',
            'options': ['Складывает', 'Возводит в степень', 'Возвращает длину', 'Удаляет'],
            'correct': 2},

            {'q': 'Какой оператор сравнения?',
            'options': ['=', '==', '=>', '=<'],
            'correct': 1},

            {'q': 'Как проверить равенство?',
            'options': ['=', '==', 'is', 'equals'],
            'correct': 1},

            {'q': 'Что такое True в Python?',
            'options': ['Строка', 'Число', 'Логическое значение', 'Список'],
            'correct': 2},

            {'q': 'Какой метод добавляет элемент в список?',
            'options': ['add()', 'append()', 'push()', 'insert()'],
            'correct': 1},

            {'q': 'Что выведет print(type(5))?',
            'options': [
                '&lt;class \"int\"&gt;',
                '&lt;class \"str\"&gt;',
                '&lt;class \"float\"&gt;',
                '&lt;class \"bool\"&gt;'
            ],
            'correct': 0},

            {'q': 'Какой символ комментария в Python?',
             'options': ['//', '#', '/* */', '--'],
            'correct': 1},
        ],
        'Средний': [],
        'Высокий': []
    },
    'JavaScript': {'Легкий': [], 'Средний': [], 'Высокий': []},
    'HTML/CSS': {'Легкий': [], 'Средний': [], 'Высокий': []}
}


def load_scores():
    if SCORES_FILE.exists():
        with open(SCORES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_scores(scores):
    with open(SCORES_FILE, 'w', encoding='utf-8') as f:
        json.dump(scores, f, ensure_ascii=False, indent=4)


def get_week_number():
    return datetime.now().isocalendar()[1]


def get_random_motivation():
    return random.choice(MOTIVATION)
