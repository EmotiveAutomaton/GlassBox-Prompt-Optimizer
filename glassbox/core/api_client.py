"""
Boeing API Client - Compliant with Boeing Internal Technical Compliance Standard v1.0

This module implements the API interface for the Boeing AI Gateway (bcai-public-api).
All requests follow the strict schema and authentication requirements.
"""

import os
import json
import uuid
import base64
import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union
from queue import Queue

import requests

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Standard message format for API communication."""
    role: str  # "user", "assistant", "system"
    content: Union[str, List[Dict[str, str]]]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API-compatible dict format."""
        if isinstance(self.content, str):
            # Typed format (preferred for safety per Boeing spec 1.4)
            return {
                "role": self.role,
                "content": [{"type": "text", "text": self.content}]
            }
        return {"role": self.role, "content": self.content}


@dataclass
class APIResponse:
    """Parsed response from Boeing API."""
    success: bool
    content: str = ""
    error_message: str = ""
    raw_response: Optional[Dict] = None


@dataclass 
class APIConfig:
    """Configuration for Boeing API client."""
    base_url: str = "https://bcai-test.web.boeing.com"
    endpoint: str = "/bcai-public-api/conversation"
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    ca_bundle_path: Optional[str] = None
    timeout: int = 60


class BoeingAPIClient:
    """
    Boeing-compliant API client for the AI Gateway.
    
    Implements all requirements from Boeing Internal Technical Compliance Standard:
    - PAT authentication via Base64-encoded Authorization header
    - Strict request body schema with mandatory fields
    - Response parsing with fallback logic
    - SSL/Certificate handling for internal CA
    - Daemon thread execution with stop signal support
    """

    def __init__(self, config: Optional[APIConfig] = None):
        self.config = config or APIConfig()
        self._conversation_guid = str(uuid.uuid4())
        self._stop_requested = threading.Event()
        self._result_queue: Queue = Queue()
        
    @property
    def pat_token(self) -> Optional[str]:
        """Retrieve PAT from environment variable (BCAI_PAT_B64)."""
        token = os.environ.get("BCAI_PAT_B64", "")
        # Strip whitespace per Boeing spec 1.2
        return token.strip() if token else None

    def _get_headers(self) -> Dict[str, str]:
        """Build compliant request headers."""
        if not self.pat_token:
            raise ValueError("BCAI_PAT_B64 environment variable not set")
        
        return {
            "Authorization": f"Basic {self.pat_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _build_request_body(
        self,
        messages: List[Message],
        temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Build request body per Boeing spec 1.3.
        
        All fields are mandatory - the API rejects omissions.
        """
        return {
            "model": self.config.model,
            "conversation_guid": self._conversation_guid,
            "stream": False,  # Strictly disabled per spec
            "skip_db_save": True,  # Mandatory per spec
            "conversation_mode": ["non-rag"],  # Mandatory per spec
            "temperature": temperature or self.config.temperature,
            "messages": [msg.to_dict() for msg in messages]
        }

    def _parse_response(self, response: requests.Response) -> APIResponse:
        """
        Parse API response with fallback logic per Boeing spec 1.5.
        
        Handles:
        - List content (iterate and join text items)
        - String content (use directly)
        - HTML responses (firewall/SSO redirect detection)
        """
        try:
            # Guard: Check for HTML (firewall/SSO redirect)
            content_type = response.headers.get("Content-Type", "")
            if "text/html" in content_type:
                return APIResponse(
                    success=False,
                    error_message="Received HTML response - likely firewall or SSO redirect. Check VPN/authentication."
                )

            data = response.json()
            
            # Primary path: response['choices'][0]['messages'][0]['content']
            # Note: Boeing API may return a list of messages in choices
            choices = data.get("choices", [])
            if not choices:
                return APIResponse(
                    success=False,
                    error_message="No choices in response",
                    raw_response=data
                )

            # Handle both message formats
            choice = choices[0]
            messages = choice.get("messages", [choice.get("message", {})])
            if isinstance(messages, dict):
                messages = [messages]
            
            if not messages:
                return APIResponse(
                    success=False,
                    error_message="No messages in response",
                    raw_response=data
                )

            content = messages[0].get("content", "")
            
            # Content extraction fallback
            if isinstance(content, list):
                # Join text items
                text_parts = [
                    item.get("text", "") 
                    for item in content 
                    if item.get("type") == "text"
                ]
                content = "".join(text_parts)
            
            return APIResponse(
                success=True,
                content=content,
                raw_response=data
            )

        except json.JSONDecodeError:
            return APIResponse(
                success=False,
                error_message="Invalid JSON response from API"
            )
        except Exception as e:
            return APIResponse(
                success=False,
                error_message=f"Response parsing error: {str(e)}"
            )

    def _handle_http_error(self, status_code: int) -> str:
        """
        Translate HTTP status codes to user-guided actions per Boeing spec Section 4.
        """
        error_messages = {
            401: "Unauthorized - Check PAT format (must be Base64 encoded, no whitespace)",
            403: "Access Denied - Check network access/VPN connection",
        }
        
        if status_code in error_messages:
            return error_messages[status_code]
        elif 300 <= status_code < 400:
            return "Redirect detected - Likely SSO interception. Authenticate via browser or check VPN."
        elif status_code >= 500:
            return f"Server error ({status_code}) - Will retry with exponential backoff"
        else:
            return f"HTTP error: {status_code}"

    def send_message(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_retries: int = 5
    ) -> APIResponse:
        """
        Send a message to the Boeing API.
        
        Implements exponential backoff for 5xx errors per Boeing spec Section 4.
        """
        url = f"{self.config.base_url}{self.config.endpoint}"
        headers = self._get_headers()
        body = self._build_request_body(messages, temperature)
        
        # SSL verification - use custom CA bundle if provided
        verify = self.config.ca_bundle_path or True
        
        backoff = 2  # Start at 2s, double up to 32s
        
        for attempt in range(max_retries):
            if self._stop_requested.is_set():
                return APIResponse(
                    success=False,
                    error_message="Request cancelled by user"
                )
            
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=body,
                    verify=verify,
                    timeout=self.config.timeout
                )
                
                if response.status_code == 200:
                    return self._parse_response(response)
                
                error_msg = self._handle_http_error(response.status_code)
                
                # Retry with backoff for 5xx errors
                if response.status_code >= 500 and attempt < max_retries - 1:
                    logger.warning(f"Server error, retrying in {backoff}s...")
                    time.sleep(backoff)
                    backoff = min(backoff * 2, 32)
                    continue
                
                return APIResponse(
                    success=False,
                    error_message=error_msg
                )
                
            except requests.exceptions.SSLError as e:
                return APIResponse(
                    success=False,
                    error_message=f"SSL Error - Check CA bundle path. Error: {str(e)}"
                )
            except requests.exceptions.Timeout:
                return APIResponse(
                    success=False,
                    error_message=f"Request timeout after {self.config.timeout}s"
                )
            except requests.exceptions.RequestException as e:
                return APIResponse(
                    success=False,
                    error_message=f"Request failed: {str(e)}"
                )
        
        return APIResponse(
            success=False,
            error_message="Max retries exceeded"
        )

    def send_message_async(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        callback: Optional[callable] = None
    ) -> threading.Thread:
        """
        Send message in a daemon thread per Boeing spec 2.3.
        
        Results are placed in _result_queue or passed to callback.
        """
        def _worker():
            result = self.send_message(messages, temperature)
            self._result_queue.put(result)
            if callback:
                callback(result)
        
        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
        return thread

    def request_stop(self):
        """Signal stop to any running async operations."""
        self._stop_requested.set()

    def reset_stop(self):
        """Reset stop signal for new operations."""
        self._stop_requested.clear()

    def new_conversation(self):
        """Start a new conversation (generates new GUID)."""
        self._conversation_guid = str(uuid.uuid4())

    def health_check(self) -> str:
        """Quick connectivity check."""
        if not self.pat_token:
            return "ERROR: BCAI_PAT_B64 environment variable not set"
        
        try:
            test_msg = Message(role="user", content="ping")
            response = self.send_message([test_msg])
            if response.success:
                return "OK"
            return f"ERROR: {response.error_message}"
        except Exception as e:
            return f"ERROR: {str(e)}"
