# Python para IA: do modelo à API

Projeto didático da live **"Python para IA: do modelo à API e integração com LLMs"**.

Quatro etapas independentes, na ordem em que o código evolui:

| Arquivo | O que mostra |
| --- | --- |
| `01_chamada_simples.py` | A chamada mínima ao LLM, com a resposta impressa no terminal |
| `02_saida_estruturada.py` | `with_structured_output` + Pydantic: o modelo devolve JSON tipado |
| `03_agente_com_tool.py` | Agente com *tool calling* sobre dados mockados em memória |
| `04_api_fastapi.py` | O agente empacotado em uma API HTTP com docs em `/docs` |

Cada arquivo roda sozinho, sem depender dos outros.

## Requisitos

- Python 3.11+
- Uma chave da [OpenRouter](https://openrouter.ai/keys)

## Setup

```powershell
python -m venv .venv #ou uv venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt #ou uv pip install -r requirements.txt
```

Em Linux/macOS, a ativação é `source .venv/bin/activate`.

Copie `.env.example` para `.env` e preencha:

```env
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=deepseek/deepseek-v4.1-flash-1017
```

> O modelo escolhido precisa aceitar *tool calling* e *structured output* — o default
> `deepseek/deepseek-v4.1-flash-1017` aceita os dois. Troque o valor para usar outro modelo.

## Rodando cada etapa

```powershell
python 01_chamada_simples.py
python 02_saida_estruturada.py
python 03_agente_com_tool.py
```

A etapa 3 imprime no console cada tool chamada pelo agente, por exemplo:

```text
-> tool consultar_pedido({'pedido_id': '1024'})
<- retorno consultar_pedido: {"status": "em transporte", ...}
```

## Etapa 4: a API

```powershell
uvicorn 04_api_fastapi:app --reload
```
Se não funcionar por conta de syntax ou falta de algum recurso, tente chamar assim na raiz do repositório, aproveitando o venv:
```powershell
.\.venv\Scripts\uvicorn.exe 04_api_fastapi:app --reload
```

Abra <http://127.0.0.1:8000/docs> e teste o `POST /chat` direto pela interface.

Teste rápido com curl:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"mensagem": "Meu pedido 1024 já chegou? E vocês têm mouse gamer em estoque?"}'
```

No PowerShell:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/chat -Method Post `
  -ContentType "application/json" `
  -Body '{"mensagem": "Meu pedido 1024 já chegou? E vocês têm mouse gamer em estoque?"}'
```

Resposta (o texto varia):

```json
{
  "resposta": "Seu pedido 1024 está em transporte...",
  "tools_acionadas": ["consultar_pedido", "verificar_estoque"],
  "modelo": "openai/gpt-4o-mini"
}
```
