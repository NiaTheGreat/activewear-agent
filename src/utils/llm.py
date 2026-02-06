"""Claude API wrapper with retry logic and error handling."""

import time
from typing import Any, Dict, List, Optional

from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings


class ClaudeClient:
    """Wrapper for Claude API with built-in retry logic and error handling."""

    # Claude Sonnet 4.5 pricing (per million tokens)
    INPUT_COST_PER_MILLION = 3.00  # $3 per 1M input tokens
    OUTPUT_COST_PER_MILLION = 15.00  # $15 per 1M output tokens

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude client.

        Args:
            api_key: Anthropic API key (defaults to settings)
        """
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")

        self.client = Anthropic(api_key=self.api_key)
        self.model = settings.CLAUDE_MODEL

        # Cost tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0

    @retry(
        stop=stop_after_attempt(settings.MAX_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def create_message(
        self,
        messages: List[Dict[str, Any]],
        system: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 1.0,
    ) -> Any:
        """
        Create a message with Claude API.

        Args:
            messages: List of message dictionaries
            system: Optional system prompt
            tools: Optional list of tool definitions
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)

        Returns:
            API response object
        """
        params = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens or settings.MAX_TOKENS_PER_REQUEST,
            "temperature": temperature,
        }

        if system:
            params["system"] = system

        if tools:
            params["tools"] = tools

        response = self.client.messages.create(**params)

        # Track token usage and cost
        self._track_usage(response)

        return response

    def create_message_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        system: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> Any:
        """
        Create a message with tool use enabled.

        Args:
            messages: Conversation messages
            tools: Tool definitions
            system: Optional system prompt
            max_tokens: Maximum tokens in response

        Returns:
            API response object
        """
        return self.create_message(
            messages=messages, system=system, tools=tools, max_tokens=max_tokens
        )

    def extract_text_response(self, response: Any) -> str:
        """
        Extract text content from API response.

        Args:
            response: API response object

        Returns:
            Text content as string
        """
        for block in response.content:
            if block.type == "text":
                return block.text
        return ""

    def extract_tool_use(self, response: Any) -> List[Dict[str, Any]]:
        """
        Extract tool use blocks from API response.

        Args:
            response: API response object

        Returns:
            List of tool use dictionaries
        """
        tool_uses = []
        for block in response.content:
            if block.type == "tool_use":
                tool_uses.append(
                    {"id": block.id, "name": block.name, "input": block.input}
                )
        return tool_uses

    def _track_usage(self, response: Any) -> None:
        """
        Track token usage and calculate costs.

        Args:
            response: API response object
        """
        if hasattr(response, "usage"):
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            self.total_input_tokens += input_tokens
            self.total_output_tokens += output_tokens

            # Calculate cost for this request
            input_cost = (input_tokens / 1_000_000) * self.INPUT_COST_PER_MILLION
            output_cost = (output_tokens / 1_000_000) * self.OUTPUT_COST_PER_MILLION
            self.total_cost += input_cost + output_cost

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get current usage statistics.

        Returns:
            Dictionary with usage stats
        """
        return {
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost": self.total_cost,
        }

    def reset_usage(self) -> None:
        """Reset usage tracking."""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0

    @staticmethod
    def format_tool_result(tool_use_id: str, result: Any) -> Dict[str, Any]:
        """
        Format tool result for conversation.

        Args:
            tool_use_id: ID of the tool use
            result: Result from tool execution

        Returns:
            Formatted tool result dictionary
        """
        return {
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": str(result),
        }


# Global client instance
_client: Optional[ClaudeClient] = None


def get_client() -> ClaudeClient:
    """
    Get or create the global Claude client instance.

    Returns:
        ClaudeClient instance
    """
    global _client
    if _client is None:
        _client = ClaudeClient()
    return _client
