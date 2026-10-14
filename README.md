# whiper-local

Ditado por voz para Windows: você aperta uma hotkey, fala, e o texto transcrito aparece onde estiver o cursor, em qualquer aplicativo.

A gravação é feita localmente. A transcrição é feita na nuvem com Whisper, pela API da **Groq** (padrão, rápida e barata) ou da **OpenAI**. O app roda em segundo plano com um ícone na bandeja do sistema que mostra o estado atual.

## Funcionalidades

- **Hotkey global** configurável (ex.: `ctrl+shift+space`, `f13`)
- **Dois modos de gravação**
  - `ptt` (push-to-talk): grava enquanto a hotkey estiver pressionada e transcreve quando você solta
  - `toggle`: aperta uma vez para começar e outra vez para parar
- **Dois modos de saída**
  - `paste`: cola o texto na janela ativa (simula `Ctrl+V`) e depois restaura o conteúdo anterior da área de transferência
  - `clipboard_only`: só copia o texto para a área de transferência
- **Feedback sonoro**: um bipe agudo quando começa a gravar e um grave quando para
- **Ícone na bandeja do sistema** com a cor do estado:

  | Cor | Estado |
  |---|---|
  | 🔵 Azul | Pronto |
  | 🔴 Vermelho | Gravando |
  | 🟠 Laranja | Transcrevendo |
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

Depois edite o `.env` e coloque a sua API key.

## Configuração

Toda a configuração fica no arquivo `.env`:

| Variável | Valores | Padrão | Descrição |
|---|---|---|---|
| `API_PROVIDER` | `groq`, `openai` | `groq` | Serviço de transcrição |
| `API_KEY` | — | **obrigatória** | Chave da API do provedor |
| `MODEL` | Groq: `whisper-large-v3-turbo`, `whisper-large-v3`. OpenAI: `whisper-1` | **obrigatório** | Modelo Whisper |
| `HOTKEY` | Qualquer combinação aceita pela lib [`keyboard`](https://github.com/boppreh/keyboard) | **obrigatória** | Atalho para gravar |
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

Se faltar alguma variável ou algum valor for inválido, o app encerra logo na inicialização e informa qual é o problema.

## Uso

### Com console (útil para ver os logs)

```powershell
.venv\Scripts\python.exe main.py
```

### Em segundo plano, sem janela

Dê um duplo clique no `start.vbs`. Ele roda o app com `pythonw.exe`, então nenhum console é aberto.

> ⚠️ O `start.vbs` tem o caminho `C:\DEV\whiper-local` fixo no código. Se o projeto estiver em outra pasta, altere esse caminho.

Para iniciar junto com o Windows, crie um atalho para o `start.vbs` em `shell:startup` (Win+R → `shell:startup`).

### Sair

Clique com o botão direito no ícone da bandeja do sistema e escolha **Exit**.

## Como funciona

```
Hotkey ──► Recorder ──► Transcriber ──► OutputHandler
 (keyboard)  (sounddevice,   (API Whisper     (pyperclip +
             16 kHz mono     Groq/OpenAI)      Ctrl+V)
             → WAV)
                 │
                 └──► TrayIcon (estado: pronto/gravando/transcrevendo/erro)
```

| Arquivo | Responsabilidade |
|---|---|
| [main.py](main.py) | Inicialização: carrega a config, conecta os componentes e inicia o ícone da bandeja |
| [src/config.py](src/config.py) | Lê e valida o `.env` e define o `base_url` da Groq |
| [src/hotkeys.py](src/hotkeys.py) | Registra a hotkey, controla o ciclo gravar → transcrever → enviar e toca os bipes |
| [src/recorder.py](src/recorder.py) | Captura o áudio do microfone (16 kHz, mono, int16) e devolve em WAV |
| [src/transcriber.py](src/transcriber.py) | Envia o WAV para a API de transcrição (cliente `openai`, compatível com a Groq) |
| [src/output.py](src/output.py) | Cola o texto na janela ativa ou só copia para a área de transferência |
| [src/tray.py](src/tray.py) | Ícone da bandeja do sistema com a cor de cada estado e o menu de saída |

A transcrição roda em uma thread separada para não travar a hotkey.

## Limitações e observações

- **A transcrição não é local.** Apesar do nome, o áudio é enviado para a Groq ou para a OpenAI. Cada requisição conta na sua cota da API.
- **O idioma está fixo em português** (`language="pt"` em [src/transcriber.py](src/transcriber.py)). Para outro idioma, altere esse valor.
- **Só funciona no Windows**, por causa do `winsound` e do comportamento da lib `keyboard`.
- **Apps rodando como administrador:** a lib `keyboard` pode não capturar a hotkey nem colar texto nessas janelas, a menos que o whiper-local também rode como administrador.
- **Modo `ptt` com combinações:** a gravação para quando você solta a *última* tecla da combinação (ex.: `space` em `ctrl+shift+space`).
- A hotkey é suprimida (`suppress=True`), então a combinação não chega aos outros aplicativos enquanto o app estiver rodando.

## Licença

[MIT](LICENSE) © 2026 tiagosantosp
