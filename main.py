import asyncio
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from helper import QUESTIONS, MOTIVATION, load_scores, save_scores, get_week_number, get_random_motivation
from api_token import TOKEN 

bot = Bot(token=TOKEN)
dp = Dispatcher()




main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Пройти тест")],
        [KeyboardButton(text="🤖 ИИ-ассистент")],
        [KeyboardButton(text="ℹ️ О боте")],
        [KeyboardButton(text="🏆 Рейтинг топ-10")]
    ],
    resize_keyboard=True
)

back_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_menu")]
])

languages_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🐍 Python", callback_data="lang_Python")],
    [InlineKeyboardButton(text="⚡ JavaScript", callback_data="lang_JavaScript")],
    [InlineKeyboardButton(text="🌐 HTML/CSS", callback_data="lang_HTML/CSS")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
])

levels_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🟢 Легкий", callback_data="level_Легкий")],
    [InlineKeyboardButton(text="🟡 Средний", callback_data="level_Средний")],
    [InlineKeyboardButton(text="🔴 Высокий", callback_data="level_Высокий")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
])

assistant_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Как лучше пройти тест?", callback_data="assist_how_test")],
    [InlineKeyboardButton(text="Какие плюсы у бота?", callback_data="assist_benefits")],
    [InlineKeyboardButton(text="Что учить дальше в Python?", callback_data="assist_python_next")],
    [InlineKeyboardButton(text="Где брать проекты для портфолио?", callback_data="assist_projects")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
])




class TestStates(StatesGroup):
    language = State()
    level = State()
    pseudonym = State()
    question = State()





def html_escape(text: str) -> str:
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;"))





@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "<b>Добро пожаловать в SkillTest Bot! 🚀</b>\n\n"
        "Я помогу тебе проверить навыки программирования, получить честный результат и заряд мотивации!\n\n"
        "Выбери действие ниже 👇",
        reply_markup=main_menu,
        parse_mode="HTML"
    )



@dp.message(F.text == "📝 Пройти тест")
async def start_test(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("<b>Выбери язык программирования:</b>", reply_markup=languages_kb, parse_mode="HTML")
    await state.set_state(TestStates.language)




@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await callback.message.edit_text("<b>SkillTest Bot</b> — твой личный тренажёр по программированию! 📚", parse_mode="HTML")
    except:
        await callback.message.answer("<b>SkillTest Bot</b> — твой личный тренажёр по программированию! 📚", parse_mode="HTML")
    await callback.message.answer("Главное меню:", reply_markup=main_menu)
    await callback.answer("Вернулись в главное меню!")




@dp.callback_query(TestStates.language, F.data.startswith("lang_"))
async def choose_level(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(language=lang)
    await callback.message.edit_text("<b>Отлично! Теперь выбери уровень сложности:</b>", reply_markup=levels_kb, parse_mode="HTML")
    await state.set_state(TestStates.level)
    await callback.answer()



@dp.callback_query(TestStates.level, F.data.startswith("level_"))
async def choose_pseudonym(callback: CallbackQuery, state: FSMContext):
    lang_data = await state.get_data()
    lang = lang_data.get('language')
    level = callback.data.split("_")[1]
    await state.update_data(level=level, current_question=0, correct=0, answers=[])

    questions_pool = QUESTIONS.get(lang, {}).get(level, [])
    if len(questions_pool) < 10:
        await callback.message.answer("Саволҳо барои ин сатҳ кам ҳастанд 😔")
        await state.clear()
        return

    selected_questions = random.sample(questions_pool, 10)
    await state.update_data(selected_questions=selected_questions)

    await callback.message.edit_text(
        "<b>Введи свой псевдоним для рейтинга</b>\n(или нажми Enter — будет использован твой username):",
        reply_markup=back_button,
        parse_mode="HTML"
    )
    await state.set_state(TestStates.pseudonym)
    await callback.answer()

@dp.message(TestStates.pseudonym)
async def set_pseudonym_and_start(message: Message, state: FSMContext):
    pseudonym = message.text.strip() or message.from_user.username or f"User_{message.from_user.id}"
    await state.update_data(pseudonym=pseudonym)
    await message.answer(f"🔥 {html_escape(pseudonym)}, начинаем тест! Удачи! 🍀")
    await send_question(message, state)




async def send_question(message, state):
    data = await state.get_data()
    q_num = data.get('current_question', 0)
    questions = data.get('selected_questions', [])

    if q_num >= len(questions):
        await finish_test(message, state)
        return

    question = questions[q_num]

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=opt, callback_data=f'ans_{i}') for i, opt in enumerate(question['options'])],
        [InlineKeyboardButton(text="🚫 Прервать тест", callback_data='stop_test')],
        [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data='back_to_menu')]
    ])

    await message.answer(
        f"<b>Вопрос {q_num + 1}/10</b>\n\n{question['q']}",
        reply_markup=kb,
        parse_mode="HTML"
    )

    await state.update_data(current_question=q_num + 1, last_question=question)




@dp.callback_query(F.data.startswith('ans_'))
async def process_answer(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    question = data.get('last_question')

    if not question:
        await callback.answer("Ошибка: вопрос не найден 😔")
        await callback.message.answer("Произошла ошибка с вопросом. Пожалуйста, начните тест заново.", reply_markup=main_menu)
        await state.clear()
        return

    ans_idx = int(callback.data.split('_')[1])
    is_correct = ans_idx == question['correct']

    data['correct'] = data.get('correct', 0) + (1 if is_correct else 0)
    data['answers'] = data.get('answers', []) + [(question['q'], question['options'][question['correct']], question['options'][ans_idx], is_correct)]
    await state.set_data(data)
    await callback.message.delete()
    await send_question(callback.message, state)
    await callback.answer()





@dp.callback_query(F.data == 'stop_test')
async def stop_test(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await finish_test(callback.message, state)
    await callback.answer("Тест прерван")





async def finish_test(message: Message, state: FSMContext):
    data = await state.get_data()
    score = data.get("correct", 0)
    total = len(data.get("selected_questions", []))
    answers = data.get("answers", [])

    result_text = "<b>Твой результат в SkillTest Bot</b>\n\n"
    result_text += f"Баллы: <b>{score}/{total}</b>\n\n"

    for q, correct_opt, user_opt, is_correct in answers:
        q_escaped = html_escape(q)
        user_opt_escaped = html_escape(user_opt)
        correct_opt_escaped = html_escape(correct_opt)
        status = '✅' if is_correct else '❌'
        result_text += f"{q_escaped}\nТвой ответ: {user_opt_escaped} {status}\nПравильный: {correct_opt_escaped}\n\n"

    motivation = html_escape(get_random_motivation())
    result_text += f"<b>Мотивация от бота:</b> {motivation}"

    scores = load_scores()
    scores.append({
        'pseudonym': data['pseudonym'],
        'score': score,
        'week': get_week_number(),
        'date': datetime.now().strftime("%Y-%m-%d")
    })
    save_scores(scores)

    await message.answer(result_text, parse_mode="HTML", reply_markup=main_menu)
    await state.clear()





@dp.message(F.text == "🤖 ИИ-ассистент")
async def ai_assistant(message: Message):
    await message.answer("<b>Задай вопрос или выбери тему:</b>", reply_markup=assistant_kb, parse_mode="HTML")




@dp.callback_query(F.data.startswith("assist_"))
async def assist_answer(callback: CallbackQuery):
    answers = {
        'how_test': 'Нажми "Пройти тест", выбери язык и уровень. Отвечай честно — бот покажет, где подтянуться! 📚',
        'benefits': 'Честная проверка, мотивация, рейтинг, советы от ИИ и прогресс твоих навыков! 🌟',
        'python_next': 'После основ изучи: функции, классы, модули, библиотеки (pandas, requests).',
        'projects': 'freeCodeCamp, Codewars, GitHub, YouTube-каналы "Фрилансер по жизни", "selfedu".'
    }
    key = callback.data.split("_")[1]
    await callback.message.edit_text(answers.get(key, 'Вопрос не найден 😅'), parse_mode="HTML")
    await callback.answer()




@dp.message(F.text == "ℹ️ О боте")
async def about_bot(message: Message):
    await message.answer(
        "<b>SkillTest Bot</b> — твой личный тренажёр по программированию! 📚\n\n"
        "Что умеет:\n"
        "• Проверять твои навыки\n"
        "• Давать честный результат с разбором ошибок\n"
        "• Мотивировать расти дальше\n"
        "• Показывать топ-10 недели\n\n"
        "Создано для студентов и всех, кто хочет стать лучше! ❤️\nВерсия 1.0",
        parse_mode="HTML"
    )



@dp.message(F.text == "🏆 Рейтинг топ-10")
async def show_rating(message: Message):
    scores = load_scores()
    current_week = get_week_number()
    weekly = [s for s in scores if s['week'] == current_week]
    top10 = sorted(weekly, key=lambda x: x['score'], reverse=True)[:10]

    if not top10:
        await message.answer("Пока никто не прошёл тест на этой неделе 😔\nБудь первым! 🔥")
        return

    text = "<b>🏆 Топ-10 на этой неделе</b>\n\n"
    for i, s in enumerate(top10, 1):
        text += f"{i}. {html_escape(s['pseudonym'])} — {s['score']} баллов\n"
    await message.answer(text, parse_mode="HTML")



async def main():
    print("SkillTest Bot!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
