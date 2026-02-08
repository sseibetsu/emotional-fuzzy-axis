import os
import google.generativeai as genai
from dotenv import load_dotenv
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Загружаем ключ из .env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("Не найден GOOGLE_API_KEY в файле .env!")

genai.configure(api_key=api_key)

# Настройка модели
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
}

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config=generation_config,
)


safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config=generation_config,
    safety_settings=safety_settings  # <-- Важно!
)


async def generate_adaptive_response(user_text: str, analysis: dict, past_context: str = "") -> str:
    """
    Формирует ответ, адаптируя тон под эмоции пользователя и учитывая память.
    """

    tone_instruction = "Будь нейтральным, вежливым и информативным."

    if analysis['graph'] == "Positive":
        intensity = analysis['x_val'] + analysis['y_val']
        if intensity > 1.5:
            tone_instruction = "Пользователь в восторге! Отвечай очень энергично, используй эмодзи, разделяй его радость. Тон: Восторженный."
        else:
            tone_instruction = "Пользователь доволен. Отвечай тепло, дружелюбно и благодарно. Тон: Дружелюбный."

    elif analysis['graph'] == "Negative":
        intensity = analysis['x_val'] + analysis['y_val']
        dominant = analysis['dominant_emotion']

        if "anger" in dominant or intensity > 1.5:
            tone_instruction = "ВНИМАНИЕ: Пользователь злится или расстроен. Твоя цель - деэскалация конфликта. Извинись, прояви эмпатию, будь максимально сдержан и конструктивен. Не спорь. Тон: Успокаивающий, Извиняющийся."
        else:
            tone_instruction = "Пользователь немного расстроен или грустит. Поддержи его, прояви мягкое участие. Тон: Заботливый, Мягкий."

    # Формируем системный промпт (инструкцию)
    prompt = f"""
    Ты - эмпатичный AI-терапевт и помощник по ментальному здоровью.
    
    ДОЛГОСРОЧНАЯ ПАМЯТЬ (Контекст прошлых бесед):
    {past_context if past_context else "Нет предыдущего контекста."}
    
    ТЕКУЩИЕ ВВОДНЫЕ ДАННЫЕ:
    Сообщение пользователя: "{user_text}"
    
    АНАЛИЗ ЭМОЦИЙ (Real-time):
    - График: {analysis['graph']}
    - Эмоция: {analysis['dominant_emotion']}
    - Интенсивность: X={analysis['x_val']}, Y={analysis['y_val']}
    
    ИНСТРУКЦИЯ ПО ТОНУ (Fuzzy Logic Controller):
    {tone_instruction}
    
    ЗАДАЧА:
    1. Проанализируй память. Если пользователь повторяется или ссылается на прошлое, используй это.
    2. Если пользователь упоминает проблему, о которой уже говорил (найдено в памяти), спроси о прогрессе.
    3. Ответь пользователю, строго соблюдая инструкцию по тону.
    """

    try:
        response = await model.generate_content_async(prompt)
        return response.text
    except Exception as e:
        return f"Ошибка генерации ответа: {str(e)}"
