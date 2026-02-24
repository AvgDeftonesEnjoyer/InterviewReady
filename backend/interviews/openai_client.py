import openai
from django.conf import settings
import logging
import time
from typing import Optional
from openai import RateLimitError, APIConnectionError, APITimeoutError, InternalServerError

logger = logging.getLogger(__name__)

# Configuration for retry logic
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds
TIMEOUT_SECONDS = 30  # Request timeout


class OpenAIError(Exception):
    """Base exception for OpenAI-related errors."""
    pass


class OpenAIRateLimitError(OpenAIError):
    """Raised when OpenAI rate limit is exceeded (429)."""
    pass


class OpenAIConnectionError(OpenAIError):
    """Raised when there's a connection issue with OpenAI API."""
    pass


class OpenAITimeoutError(OpenAIError):
    """Raised when OpenAI request times out."""
    pass


class OpenAIServerError(OpenAIError):
    """Raised when OpenAI returns a server error (500, 503, etc.)."""
    pass


def get_ai_response(system_prompt: str, messages: list, retry_count: int = 0) -> str:
    """
    Send conversation to GPT-4o-mini and get AI response.
    
    Features:
    - Retry logic with exponential backoff
    - Timeout handling
    - Rate limit handling (429)
    - Connection error handling
    - Comprehensive logging
    """
    client = openai.OpenAI(
        api_key=settings.OPENAI_API_KEY,
        timeout=TIMEOUT_SECONDS
    )

    # Keep only last 12 messages to save tokens
    history = messages[-12:]

    try:
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {'role': 'system', 'content': system_prompt},
                *history
            ],
            max_tokens=300,  # Increased from 150 for better responses
            temperature=0.7,
        )
        
        if not response.choices or not response.choices[0].message.content:
            logger.warning("OpenAI returned empty response")
            return "I apologize, but I'm having trouble generating a response. Could you please try again?"
        
        content = response.choices[0].message.content.strip()
        logger.info(f"OpenAI response received ({len(content)} chars)")
        return content
        
    except RateLimitError as e:
        # Handle rate limiting (429)
        logger.warning(f"OpenAI rate limit exceeded: {str(e)}")
        
        if retry_count < MAX_RETRIES:
            # Exponential backoff: wait 1s, 2s, 4s...
            wait_time = RETRY_DELAY * (2 ** retry_count)
            logger.info(f"Retrying in {wait_time} seconds... (attempt {retry_count + 1}/{MAX_RETRIES})")
            time.sleep(wait_time)
            return get_ai_response(system_prompt, messages, retry_count + 1)
        
        raise OpenAIRateLimitError(
            "AI service is currently experiencing high demand. Please try again in a few minutes."
        )
        
    except APITimeoutError as e:
        logger.error(f"OpenAI request timed out: {str(e)}")
        raise OpenAITimeoutError(
            "AI service request timed out. Please check your connection and try again."
        )
        
    except APIConnectionError as e:
        logger.error(f"OpenAI connection error: {str(e)}")
        raise OpenAIConnectionError(
            "Unable to connect to AI service. Please check your internet connection."
        )
        
    except InternalServerError as e:
        logger.error(f"OpenAI server error: {str(e)}")
        raise OpenAIServerError(
            "AI service is temporarily unavailable. Please try again later."
        )
        
    except Exception as e:
        logger.error(f"Unexpected OpenAI error: {type(e).__name__} - {str(e)}")
        raise OpenAIError(f"An unexpected error occurred while processing your request: {str(e)}")


def transcribe_audio(audio_file, retry_count: int = 0) -> str:
    """
    Transcribe audio using OpenAI Whisper.
    
    Features:
    - Retry logic with exponential backoff
    - Timeout handling
    - Rate limit handling
    - Comprehensive logging
    """
    client = openai.OpenAI(
        api_key=settings.OPENAI_API_KEY,
        timeout=TIMEOUT_SECONDS
    )

    try:
        logger.info(f"Starting audio transcription (file size: {audio_file.size if hasattr(audio_file, 'size') else 'unknown'})")
        
        transcript = client.audio.transcriptions.create(
            model='whisper-1',
            file=audio_file,
            language='en',  # Optional: specify language if known
        )
        
        if not transcript or not transcript.text:
            logger.warning("Whisper returned empty transcription")
            return ""
        
        text = transcript.text.strip()
        logger.info(f"Audio transcription completed ({len(text)} chars)")
        return text
        
    except RateLimitError as e:
        logger.warning(f"OpenAI rate limit exceeded for transcription: {str(e)}")
        
        if retry_count < MAX_RETRIES:
            wait_time = RETRY_DELAY * (2 ** retry_count)
            logger.info(f"Retrying transcription in {wait_time} seconds...")
            time.sleep(wait_time)
            return transcribe_audio(audio_file, retry_count + 1)
        
        raise OpenAIRateLimitError(
            "Transcription service is busy. Please try again in a few minutes."
        )
        
    except APITimeoutError as e:
        logger.error(f"Transcription request timed out: {str(e)}")
        raise OpenAITimeoutError(
            "Audio transcription timed out. Please try a shorter audio clip."
        )
        
    except APIConnectionError as e:
        logger.error(f"Transcription connection error: {str(e)}")
        raise OpenAIConnectionError(
            "Unable to connect to transcription service."
        )
        
    except Exception as e:
        logger.error(f"Unexpected transcription error: {type(e).__name__} - {str(e)}")
        raise OpenAIError(f"Transcription failed: {str(e)}")
