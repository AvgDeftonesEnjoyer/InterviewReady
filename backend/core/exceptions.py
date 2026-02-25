from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging
from interviews.openai_client import (
    OpenAIError, OpenAIRateLimitError, OpenAITimeoutError, 
    OpenAIConnectionError, OpenAIServerError
)

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Global exception handler for DRF to cleanly manage OpenAI errors and other exceptions
    without muddying the API Views with try-except blocks.
    """
    # Call REST framework's default exception handler to handle standard DRF exceptions
    response = exception_handler(exc, context)

    # If it's an OpenAI specific error, we return a custom response and status code
    if isinstance(exc, OpenAIRateLimitError):
        logger.warning(f"Rate limit error: {str(exc)}")
        return Response({
            'error': 'ai_rate_limit',
            'message': str(exc)
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
    elif isinstance(exc, OpenAITimeoutError):
        logger.error(f"Timeout error: {str(exc)}")
        return Response({
            'error': 'ai_timeout',
            'message': str(exc)
        }, status=status.HTTP_504_GATEWAY_TIMEOUT)
        
    elif isinstance(exc, OpenAIConnectionError):
        logger.error(f"Connection error: {str(exc)}")
        return Response({
            'error': 'ai_connection_error',
            'message': str(exc)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
    elif isinstance(exc, OpenAIServerError):
        logger.error(f"Server error: {str(exc)}")
        return Response({
            'error': 'ai_server_error',
            'message': str(exc)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
    elif isinstance(exc, OpenAIError):
        logger.error(f"OpenAI error: {str(exc)}")
        return Response({
            'error': 'ai_error',
            'message': str(exc)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
