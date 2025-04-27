import os
import openai
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

print('Бот запущен!')

TOKEN = "tg token"
OPENAI_API_KEY = "open ai token" 

bot = Bot(token=TOKEN)
dp = Dispatcher()
openai.api_key = OPENAI_API_KEY

NUMBERS_ROWS = 200
CONTEXT_SIZE = 100

if not os.path.exists("users"):
    os.mkdir("users")

SYSTEM_PROMPT = (
    "You are a smart assistant who selects universities for students based on their data, "
    "helps with admission, assesses their chances, and remembers all their information."
)

UNIVERSITY_KEYWORDS = {"university", "admission", "application", "scholarship", 
                       "study abroad", "GPA", "SAT", "IELTS", "TOEFL", "faculty", "САТ", "Айлтс"}

DEVELOPER_KEYWORDS = {"developer", "creator", "developer team", "team", "разработчики", "разработчик"}
PROJECT_KEYWORDS = {"project", "about the project", "what is the project", "purpose", "проект", "проекты", "о проекте"}

EDUCATION_KEYWORDS = {"education", "study", "learning", "study abroad", "обучение", "образование", "учёба", "учёба за границей"}
CAREER_KEYWORDS = {"career", "job", "profession", "work", "career advice", "профессия", "работа", "карьера", "профессиональный рост"}
LIFE_ABROAD_KEYWORDS = {"life abroad", "living abroad", "study abroad", "life in another country", "жизнь за границей", "учёба за границей", "жить за границей"}
STUDY_TIPS_KEYWORDS = {"study tips", "study advice", "study techniques", "study methods", "советы по учёбе", "методы обучения", "советы для учёбы"}
FINANCIAL_AID_KEYWORDS = {"financial aid", "scholarship", "tuition", "financial support", "финансовая помощь", "стипендия", "оплата обучения"}

DEVELOPER_INFO = "This bot was developed by Sanzhar Kustavletov."
PROJECT_INFO = "The project helps students with the admission process to prestigious universities. It provides personalized advice on university selection, application procedures, scholarships, and other aspects to make the process easier and more effective."

EDUCATION_INFO = "This bot provides guidance and support on educational opportunities, including studying abroad, choosing the right university, and preparing for entrance exams."
CAREER_INFO = "This bot offers career advice and guidance, helping you navigate your career choices, find job opportunities, and understand key skills for success in your professional life."
LIFE_ABROAD_INFO = "This bot helps you navigate life abroad, whether it's for study or work, providing tips on adjusting to a new culture, housing, and other aspects of living in a foreign country."
STUDY_TIPS_INFO = "This bot provides helpful study tips and techniques to improve your learning efficiency, time management, and exam preparation."
FINANCIAL_AID_INFO = "This bot offers information about scholarships, financial aid, and tuition options for students, helping you manage the costs of higher education."

@dp.message(Command("clear"))
async def clear_history(message: Message):
    user_file = f"users/{message.chat.id}.txt"
    if os.path.exists(user_file):
        os.remove(user_file)
    await message.answer("History cleared!")

@dp.message()
async def handle_message(message: Message):
    user_file = f"users/{message.chat.id}.txt"

    # Ответы на вопросы о проекте
    if any(word in message.text.lower() for word in PROJECT_KEYWORDS):
        return await message.answer(PROJECT_INFO)

    # Ответы на вопросы о разработчиках
    if any(word in message.text.lower() for word in DEVELOPER_KEYWORDS):
        return await message.answer(DEVELOPER_INFO)

    # Ответы на вопросы об обучении
    if any(word in message.text.lower() for word in EDUCATION_KEYWORDS):
        return await message.answer(EDUCATION_INFO)

    # Ответы на вопросы о карьере
    if any(word in message.text.lower() for word in CAREER_KEYWORDS):
        return await message.answer(CAREER_INFO)

    # Ответы на вопросы о жизни за границей
    if any(word in message.text.lower() for word in LIFE_ABROAD_KEYWORDS):
        return await message.answer(LIFE_ABROAD_INFO)

    # Ответы на вопросы по методам обучения
    if any(word in message.text.lower() for word in STUDY_TIPS_KEYWORDS):
        return await message.answer(STUDY_TIPS_INFO)

    # Ответы на вопросы по финансовой помощи
    if any(word in message.text.lower() for word in FINANCIAL_AID_KEYWORDS):
        return await message.answer(FINANCIAL_AID_INFO)

    # Основной ответ с GPT, если нет совпадений с ключевыми словами
    history = []
    if os.path.exists(user_file):
        with open(user_file, "r", encoding="utf-8") as file:
            history = file.readlines()[-(CONTEXT_SIZE * 2):]

    formatted_history = [{"role": "user" if i % 2 == 0 else "assistant", "content": line.strip()} 
                         for i, line in enumerate(history)]

    send_message = await message.answer("Processing your request, please wait...")

    try:
        completion = await asyncio.to_thread(
            openai.ChatCompletion.create,
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + formatted_history + [
                {"role": "user", "content": message.text}
            ],
            presence_penalty=0.6
        )

        response_text = completion.choices[0].message["content"]
        await send_message.edit_text(response_text)

        with open(user_file, "a+", encoding="utf-8") as file:
            file.write(f"{message.text}\n{response_text}\n")

        with open(user_file, "r", encoding="utf-8") as file:
            lines = file.readlines()

        if len(lines) >= NUMBERS_ROWS + 1:
            with open(user_file, "w", encoding="utf-8") as file:
                file.writelines(lines[2:])

    except Exception as e:
        await message.answer(f"Error: {str(e)}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

