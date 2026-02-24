import openai
from django.conf import settings


def get_ai_response(system_prompt: str, messages: list) -> str:
    """Send conversation to GPT-4o-mini and get AI response."""
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    # Keep only last 12 messages to save tokens
    history = messages[-12:]

    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {'role': 'system', 'content': system_prompt},
            *history
        ],
        max_tokens=150,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def transcribe_audio(audio_file) -> str:
    """Transcribe audio using OpenAI Whisper."""
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    transcript = client.audio.transcriptions.create(
        model='whisper-1',
        file=audio_file,
    )
    return transcript.text
