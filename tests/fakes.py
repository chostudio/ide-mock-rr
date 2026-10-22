"""A stand-in for openai.OpenAI so tests never touch the network.

Each response is a string (the message content) or an Exception to raise.
The last response repeats once the list is used up.
"""
from types import SimpleNamespace


class FakeClient:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        r = self.responses.pop(0) if len(self.responses) > 1 else self.responses[0]
        if isinstance(r, Exception):
            raise r
        message = SimpleNamespace(content=r, refusal=None)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])
