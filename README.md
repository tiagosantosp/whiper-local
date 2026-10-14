# whiper-local

Ditado por voz para Windows: carregas numa hotkey, falas, e o texto transcrito aparece onde estiver o cursor, em qualquer aplicação.

A gravação é feita localmente. A transcrição é feita na nuvem com Whisper, pela API da **Groq** (por defeito, rápida e barata) ou da **OpenAI**. A app corre em segundo plano com um ícone na barra de sistema que mostra o estado atual.

## Funcionalidades

- **Hotkey global** configurável (ex.: `ctrl+shift+space`, `f13`)
- **Dois modos de gravação**
  - `ptt` (push-to-talk): grava enquanto a hotkey estiver premida e transcreve quando a largas
  - `toggle`: premes uma vez para começar e outra vez para parar
- **Dois modos de saída**
  - `paste`: cola o texto na janela ativa (simula `Ctrl+V`) e depois repõe o conteúdo anterior do clipboard
  - `clipboard_only`: só copia o texto para o clipboard
- **Feedback sonoro**: um bip agudo quando começa a gravar e um grave quando para
- **Ícone na barra de sistema** com a cor do estado:

  | Cor | Estado |
  |---|---|
  | 🔵 Azul | Pronto |
  | 🔴 Vermelho | A gravar |
  | 🟠 Laranja | A transcrever |
  | 🟤 Vermelho escuro | Erro |

## Requisitos

- **Windows** (usa `winsound` e a biblioteca `keyboard`)
- Python 3.10 ou mais recente
- Um microfone
- Uma API key da [Groq](https://console.groq.com/keys) ou da [OpenAI](https://platform.openai.com/api-keys)

## Instalação

```powershell
git clone <url-do-repo> whiper-local
cd whiper-local

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

copy .env.example .env
```

Depois edita o `.env` e coloca a tua API key.

## Configuração

Toda a configuração fica no ficheiro `.env`:

| Variável | Valores | Padrão | Descrição |
|---|---|---|---|
| `API_PROVIDER` | `groq`, `openai` | `groq` | Serviço de transcrição |
| `API_KEY` | — | **obrigatória** | Chave da API do provider |
| `MODEL` | Groq: `whisper-large-v3-turbo`, `whisper-large-v3`. OpenAI: `whisper-1` | **obrigatório** | Modelo Whisper |
| `HOTKEY` | Qualquer combinação aceite pela lib [`keyboard`](https://github.com/boppreh/keyboard) | **obrigatória** | Atalho para gravar |
| `HOTKEY_MODE` | `ptt`, `toggle` | `ptt` | Modo de gravação |
| `OUTPUT_MODE` | `paste`, `clipboard_only` | `paste` | O que fazer com o texto |

Exemplo:

```env
API_PROVIDER=groq
API_KEY=gsk_...
MODEL=whisper-large-v3-turbo
HOTKEY=ctrl+shift+space
HOTKEY_MODE=ptt
OUTPUT_MODE=paste
```

Se faltar alguma variável ou um valor for inválido, a app termina logo ao arrancar e indica qual é o problema.

## Utilização

### Com consola (útil para ver logs)

```powershell
.venv\Scripts\python.exe main.py
```

### Em segundo plano, sem janela

Faz duplo clique em `start.vbs`. Corre a app com `pythonw.exe`, por isso não abre nenhuma consola.

> ⚠️ O `start.vbs` tem o caminho `C:\DEV\whiper-local` escrito no código. Se o projeto estiver noutra pasta, altera esse caminho.

Para iniciar com o Windows, cria um atalho para o `start.vbs` em `shell:startup` (Win+R → `shell:startup`).

### Sair

Clica com o botão direito no ícone da barra de sistema e escolhe **Exit**.

## Como funciona

```
Hotkey ──► Recorder ──► Transcriber ──► OutputHandler
 (keyboard)  (sounddevice,   (API Whisper     (pyperclip +
             16 kHz mono     Groq/OpenAI)      Ctrl+V)
             → WAV)
                 │
                 └──► TrayIcon (estado: pronto/gravando/transcrevendo/erro)
```

| Ficheiro | Responsabilidade |
|---|---|
| [main.py](main.py) | Arranque: carrega a config, liga os componentes e inicia o ícone da bandeja |
| [src/config.py](src/config.py) | Lê e valida o `.env` e define o `base_url` da Groq |
| [src/hotkeys.py](src/hotkeys.py) | Regista a hotkey, controla o ciclo gravar → transcrever → enviar e toca os bips |
| [src/recorder.py](src/recorder.py) | Captura áudio do microfone (16 kHz, mono, int16) e devolve-o em WAV |
| [src/transcriber.py](src/transcriber.py) | Envia o WAV para a API de transcrição (cliente `openai`, compatível com a Groq) |
| [src/output.py](src/output.py) | Cola o texto na janela ativa ou só o copia para o clipboard |
| [src/tray.py](src/tray.py) | Ícone da barra de sistema com a cor de cada estado e o menu de saída |

A transcrição corre numa thread separada para não bloquear a hotkey.

## Limitações e notas

- **A transcrição não é local.** Apesar do nome, o áudio é enviado para a Groq ou para a OpenAI. Cada pedido conta para a tua quota da API.
- **O idioma está fixo em português** (`language="pt"` em [src/transcriber.py](src/transcriber.py)). Para outro idioma, altera esse valor.
- **Só funciona no Windows**, por causa do `winsound` e do comportamento da lib `keyboard`.
- **Apps a correr como administrador:** a lib `keyboard` pode não apanhar a hotkey nem colar texto nessas janelas, a não ser que o whiper-local também corra como administrador.
- **Modo `ptt` com combinações:** a gravação para quando largas a *última* tecla da combinação (ex.: `space` em `ctrl+shift+space`).
- A hotkey é suprimida (`suppress=True`), por isso a combinação deixa de chegar às outras aplicações enquanto a app estiver a correr.

## Licença

[MIT](LICENSE) © 2026 tiagosantosp
