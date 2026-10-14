import sys

import keyboard

from src.config import load_config
from src.hotkeys import HotkeyController
from src.output import OutputHandler
from src.recorder import Recorder
from src.transcriber import Transcriber
from src.tray import TrayIcon


def main() -> None:
    try:
        config = load_config()
    except ValueError as e:
        print(f"[ERRO DE CONFIG] {e}", file=sys.stderr)
        print("Copia .env.example para .env e preenche os valores.", file=sys.stderr)
        sys.exit(1)

    recorder = Recorder()
    transcriber = Transcriber(config)
    output = OutputHandler(config)

    tray = TrayIcon(on_exit=lambda: None)

    def on_exit() -> None:
        keyboard.unhook_all()
        tray.stop()

    tray._on_exit = on_exit

    controller = HotkeyController(config, recorder, transcriber, output, tray)
    controller.register()

    print(f"[INFO] whiper-local iniciado.")
    print(f"[INFO] Provider: {config.api_provider} | Modelo: {config.model}")
    print(f"[INFO] Hotkey: {config.hotkey} | Modo: {config.hotkey_mode} | Saída: {config.output_mode}")
    print("[INFO] Clica com o botão direito no ícone da barra de sistema para sair.")

    tray.run()


if __name__ == "__main__":
    main()
