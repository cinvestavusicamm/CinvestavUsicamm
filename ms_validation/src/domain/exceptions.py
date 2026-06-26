"""ms_validation.domain.exceptions

Domain-level exceptions. These are framework-agnostic; the presentation
layer maps them to HTTP status codes.
"""


class LLMOutputParseError(Exception):
    """Raised when the LLM response cannot be parsed into ValidationResult."""

    def __init__(self, raw_output: str, reason: str = ""):
        self.raw_output = raw_output
        self.reason = reason
        super().__init__(
            f"LLM output parse failed: {reason}. Raw (truncated): {raw_output[:200]}"
        )


class VRAMBusyError(Exception):
    """Raised when the semaphore could not be acquired within the timeout."""

    pass
