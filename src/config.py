from dataclasses import dataclass
from dotenv import load_dotenv
import os

VALID_PROVIDERS = {"openai", "groq"}
VALID_MODES = {"ptt", "toggle"}
VALID_OUTPUTS = {"paste", "clipboard_only"}

GROQ_BASE_URL = "https://api.groq.com/openai/v1"


@dataclass(frozen=True)
class Config:
    api_key: str
    api_provider: str
    model: str
    hotkey: str
    hotkey_mode: str
    output_mode: str
    base_url: str | None


def load_config() -> Config:
    load_dotenv()

    api_key = os.getenv("API_KEY", "").strip()
    if not api_key:
        raise ValueError("API_KEY não definida no .env")

    api_provider = os.getenv("API_PROVIDER", "groq").strip().lower()
    if api_provider not in VALID_PROVIDERS:
        raise ValueError(f"API_PROVIDER inválido: '{api_provider}'. Use: {VALID_PROVIDERS}")

    model = os.getenv("MODEL", "").strip()
    if not model:
        raise ValueError("MODEL não definido no .env")

    hotkey = os.getenv("HOTKEY", "").strip()
    if not hotkey:
        raise ValueError("HOTKEY não definida no .env")

    hotkey_mode = os.getenv("HOTKEY_MODE", "ptt").strip().lower()
    if hotkey_mode not in VALID_MODES:
        raise ValueError(f"HOTKEY_MODE inválido: '{hotkey_mode}'. Use: {VALID_MODES}")

    output_mode = os.getenv("OUTPUT_MODE", "paste").strip().lower()
    if output_mode not in VALID_OUTPUTS:
        raise ValueError(f"OUTPUT_MODE inválido: '{output_mode}'. Use: {VALID_OUTPUTS}")

    base_url = GROQ_BASE_URL if api_provider == "groq" else None

    return Config(
        api_key=api_key,
        api_provider=api_provider,
        model=model,
        hotkey=hotkey,
        hotkey_mode=hotkey_mode,
        output_mode=output_mode,
        base_url=base_url,
    )
