from collections import deque

from .client import LlmClient, LlmProvider, LlmRequest, LlmResponse


class FakeLlmClient(LlmClient):
    """
    Deterministic fake LLM client for testing.
    Maintains a queue of responses to return in order.
    """

    def __init__(self) -> None:
        self.response_queue: deque[LlmResponse | Exception] = deque()
        self.received_requests: list[LlmRequest] = []

    def add_response(self, response: LlmResponse) -> None:
        """Add a successful response to the queue."""
        self.response_queue.append(response)

    def add_error(self, error: Exception) -> None:
        """Add an error to the queue to be raised when generate is called."""
        self.response_queue.append(error)

    async def generate(self, request: LlmRequest) -> LlmResponse:
        """
        Record the request and return the next queued response/error.
        If the queue is empty, returns a default response.
        """
        self.received_requests.append(request)

        if not self.response_queue:
            # Default fallback response if none queued
            return LlmResponse(
                text="Default fake response",
                model="fake-model",
                provider=LlmProvider.FAKE,
            )

        next_item = self.response_queue.popleft()

        if isinstance(next_item, Exception):
            raise next_item

        return next_item

    def clear(self) -> None:
        """Clear the queue and history."""
        self.response_queue.clear()
        self.received_requests.clear()
