"""
Gemini API Client - Alternative backend for local development/debugging.

Uses Google's Gemini Flash model when Boeing API is unavailable.
"""

import os
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import threading

# Load .env file if present (for local development)
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

# Try to import Google GenAI SDK
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google-genai not installed. Run: pip install google-genai")


@dataclass
class GeminiConfig:
    """Configuration for Gemini API."""
    api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    model: str = "gemini-2.0-flash"
    temperature: float = 0.7
    max_tokens: int = 4096


@dataclass
class GeminiResponse:
    """Standardized response from Gemini API."""
    success: bool
    content: str = ""
    error_message: str = ""
    raw_response: Any = None


class GeminiAPIClient:
    """
    Gemini API client for local development and debugging.
    
    Drop-in replacement for BoeingAPIClient when outside Boeing network.
    """

    def __init__(self, config: Optional[GeminiConfig] = None):
        self.config = config or GeminiConfig()
        self._client = None
        self._stop_event = threading.Event()
        
        if not GENAI_AVAILABLE:
            logger.error("google-genai SDK not available")
            return
            
        if not self.config.api_key:
            logger.error("GEMINI_API_KEY environment variable not set")
            return
        
        try:
            self._client = genai.Client(api_key=self.config.api_key)
            logger.info(f"Gemini client initialized with model: {self.config.model}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")

    def send_message(
        self,
        messages: List[Any],  # Can be Message objects or dicts
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> GeminiResponse:
        """
        Send a message to Gemini API.
        
        Args:
            messages: List of message objects (compatible with Boeing Message format)
            temperature: Override temperature
            max_tokens: Override max tokens
            
        Returns:
            GeminiResponse with success status and content
        """
        if not self._client:
            return GeminiResponse(
                success=False,
                error_message="Gemini client not initialized. Check API key."
            )

        if self._stop_event.is_set():
            return GeminiResponse(
                success=False,
                error_message="Request cancelled"
            )

        try:
            # Convert messages to Gemini format
            gemini_contents = self._convert_messages(messages)
            
            # Build generation config
            gen_config = types.GenerateContentConfig(
                temperature=temperature or self.config.temperature,
                max_output_tokens=max_tokens or self.config.max_tokens,
            )

            # Make API call
            response = self._client.models.generate_content(
                model=self.config.model,
                contents=gemini_contents,
                config=gen_config
            )

            # Extract text from response
            if response.text:
                return GeminiResponse(
                    success=True,
                    content=response.text,
                    raw_response=response
                )
            else:
                return GeminiResponse(
                    success=False,
                    error_message="Empty response from Gemini",
                    raw_response=response
                )

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return GeminiResponse(
                success=False,
                error_message=str(e)
            )

    def _convert_messages(self, messages: List[Any]) -> List[types.Content]:
        """Convert Boeing-style messages to Gemini format."""
        contents = []
        system_instruction = None
        
        for msg in messages:
            # Handle both Message objects and dicts
            if hasattr(msg, 'role'):
                role = msg.role
                content = msg.content
            else:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
            
            # Extract text from content
            if isinstance(content, list):
                # Boeing format: [{"type": "text", "text": "..."}]
                text_parts = [
                    item.get('text', '') 
                    for item in content 
                    if isinstance(item, dict) and item.get('type') == 'text'
                ]
                text = "\n".join(text_parts)
            else:
                text = str(content)
            
            # Handle system messages (Gemini uses system_instruction)
            if role == 'system':
                system_instruction = text
                continue
            
            # Map roles
            gemini_role = 'user' if role == 'user' else 'model'
            
            contents.append(types.Content(
                role=gemini_role,
                parts=[types.Part(text=text)]
            ))
        
        # Prepend system instruction to first user message if present
        if system_instruction and contents:
            first_content = contents[0]
            if first_content.parts:
                original_text = first_content.parts[0].text
                contents[0] = types.Content(
                    role='user',
                    parts=[types.Part(text=f"[System: {system_instruction}]\n\n{original_text}")]
                )
        
        return contents

    def request_stop(self):
        """Request stop of pending operations."""
        self._stop_event.set()

    def reset_stop(self):
        """Reset stop signal."""
        self._stop_event.clear()

    def health_check(self) -> Dict[str, Any]:
        """Check API connectivity."""
        return {
            "available": GENAI_AVAILABLE,
            "client_initialized": self._client is not None,
            "model": self.config.model,
            "api_key_set": bool(self.config.api_key)
        }


def get_api_client(use_gemini: bool = None):
    """
    Factory function to get the appropriate API client.
    
    Args:
        use_gemini: Force Gemini (True) or Boeing (False). 
                    If None, auto-detect based on environment.
    
    Returns:
        Either GeminiAPIClient or BoeingAPIClient
    """
    if use_gemini is None:
        # Auto-detect: use Gemini if GEMINI_API_KEY is set, else try Boeing
        use_gemini = bool(os.getenv("GEMINI_API_KEY"))
    
    if use_gemini:
        return GeminiAPIClient()
    else:
        from glassbox.core.api_client import BoeingAPIClient
        return BoeingAPIClient()
