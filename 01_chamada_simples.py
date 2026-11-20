"""Etapa 1 - a chamada mais simples possível a um LLM, via OpenRouter."""

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise SystemExit("OPENROUTER_API_KEY não definida. Copie .env.example para .env e preencha a chave.")

modelo = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
)

resposta = modelo.invoke("Explique em duas frases o que é um LLM.")
print(resposta.text)
