import os
from google import genai
from google.genai import types

def ask_gemini_free(prompt: str, system_instruction: str = None) -> str:
    """
    Изолированный бесплатный вызов Gemini 2.5 Flash.
    Использует GEMINI_API_KEY из Cloud Run.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "Ошибка: GEMINI_API_KEY не установлен в Cloud Run."

    try:
        client = genai.Client(api_key=api_key)
        config = None
        if system_instruction:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction
            )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config
        )
        return response.text
    except Exception as e:
        return f"Ошибка Gemini AI Circuit: {str(e)}"
