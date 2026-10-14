from openai import OpenAI

from .config import Config


class Transcriber:
    def __init__(self, config: Config):
        self._model = config.model
        self._client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
        )

    def transcribe(self, wav_bytes: bytes) -> str:
        result = self._client.audio.transcriptions.create(
            model=self._model,
            file=("audio.wav", wav_bytes, "audio/wav"),
            response_format="text",
            language="pt",
        )
        return result.strip() if isinstance(result, str) else str(result).strip()
