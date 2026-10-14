import threading
import winsound

import keyboard

_BEEP_START = (880, 80)   # Hz, ms — tom alto curto: início de gravação
_BEEP_STOP  = (440, 120)  # Hz, ms — tom baixo curto: fim de gravação


def _beep(freq: int, duration: int) -> None:
    threading.Thread(target=winsound.Beep, args=(freq, duration), daemon=True).start()

from .config import Config
from .output import OutputHandler
from .recorder import Recorder
from .transcriber import Transcriber
from .tray import TrayIcon


class HotkeyController:
    def __init__(
        self,
        config: Config,
        recorder: Recorder,
        transcriber: Transcriber,
        output: OutputHandler,
        tray: TrayIcon,
    ):
        self._config = config
        self._recorder = recorder
        self._transcriber = transcriber
        self._output = output
        self._tray = tray
        self._recording = False

    def register(self) -> None:
        if self._config.hotkey_mode == "ptt":
            keyboard.add_hotkey(self._config.hotkey, self._ptt_start, suppress=True)
            # on_press_key/on_release_key não suportam combinações, por isso observamos
            # o release da tecla base (última parte da combinação, ex: "space" em "ctrl+shift+space")
            base_key = self._config.hotkey.split("+")[-1].strip()
            keyboard.on_release_key(base_key, self._ptt_stop, suppress=False)
        else:
            keyboard.add_hotkey(self._config.hotkey, self._toggle, suppress=True)

    def _ptt_start(self, event=None) -> None:
        if self._recording:
            return
        self._recording = True
        try:
            self._recorder.start()
            _beep(*_BEEP_START)
            self._tray.set_status("recording")
        except Exception as e:
            print(f"[ERRO] Não foi possível iniciar gravação: {e}")
            self._recording = False
            self._tray.set_status("error")

    def _ptt_stop(self, event=None) -> None:
        if not self._recording:
            return
        self._recording = False
        self._tray.set_status("transcribing")
        try:
            wav = self._recorder.stop()
            _beep(*_BEEP_STOP)
        except Exception as e:
            print(f"[ERRO] Falha ao parar gravação: {e}")
            self._tray.set_status("error")
            return
        threading.Thread(target=self._process, args=(wav,), daemon=True).start()

    def _toggle(self) -> None:
        if not self._recording:
            self._recording = True
            try:
                self._recorder.start()
                _beep(*_BEEP_START)
                self._tray.set_status("recording")
            except Exception as e:
                print(f"[ERRO] Não foi possível iniciar gravação: {e}")
                self._recording = False
                self._tray.set_status("error")
        else:
            self._recording = False
            self._tray.set_status("transcribing")
            try:
                wav = self._recorder.stop()
                _beep(*_BEEP_STOP)
            except Exception as e:
                print(f"[ERRO] Falha ao parar gravação: {e}")
                self._tray.set_status("error")
                return
            threading.Thread(target=self._process, args=(wav,), daemon=True).start()

    def _process(self, wav: bytes) -> None:
        if not wav:
            print("[AVISO] Gravação vazia, ignorando.")
            self._tray.set_status("idle")
            return
        try:
            text = self._transcriber.transcribe(wav)
            if text:
                self._output.send(text)
            else:
                print("[AVISO] Transcrição devolveu texto vazio.")
        except Exception as e:
            print(f"[ERRO] Transcrição falhou: {e}")
            self._tray.set_status("error")
            import time
            time.sleep(2)
        finally:
            self._tray.set_status("idle")
