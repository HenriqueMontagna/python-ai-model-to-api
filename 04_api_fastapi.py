"""Etapa 4 - o agente da etapa 3 empacotado como API FastAPI (docs em /docs)."""

import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from langchain.agents import create_agent
from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise SystemExit("OPENROUTER_API_KEY não definida. Copie .env.example para .env e preencha a chave.")

MODELO = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

# Mesmos dados e tools da etapa 3 (aqui repetidos para o arquivo rodar sozinho).
PEDIDOS = {
    "1024": {"status": "em transporte", "previsao_entrega": "2026-11-22", "itens": ["Kit velas aromáticas"]},
    "2048": {"status": "entregue", "previsao_entrega": None, "itens": ["Teclado mecânico"]},
    "4096": {"status": "pagamento pendente", "previsao_entrega": None, "itens": ["Mouse gamer"]},
}

ESTOQUE = {"mouse gamer": 0, "teclado mecanico": 7, "kit velas aromaticas": 32}


@tool
def consultar_pedido(pedido_id: str) -> str:
    """Busca o status de um pedido pelo ID (ex.: "1024")."""
    pedido = PEDIDOS.get(pedido_id.strip())
    if pedido is None:
        return f"Pedido '{pedido_id}' não encontrado. IDs válidos: {', '.join(PEDIDOS)}."
    return json.dumps(pedido, ensure_ascii=False)


@tool
def verificar_estoque(produto: str) -> str:
    """Informa quantas unidades de um produto existem em estoque (ex.: "mouse gamer")."""
    produto = produto.strip().lower()
    if produto not in ESTOQUE:
        return f"Produto '{produto}' não encontrado. Catálogo: {', '.join(ESTOQUE)}."
    return f"{ESTOQUE[produto]} unidade(s) de '{produto}' em estoque."


modelo = ChatOpenAI(
    model=MODELO,
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
    temperature=0,
)

agente = create_agent(
    model=modelo,
    tools=[consultar_pedido, verificar_estoque],
    system_prompt=(
        "Você é o atendimento da Loja La Montagna. Consulte as tools antes de responder "
        "sobre pedidos ou estoque. Responda em português, em poucas frases."
    ),
)

app = FastAPI(
    title="Atendimento Loja La Montagna",
    version="1.0.0",
    description="Agente LangChain com tools exposto como serviço HTTP.",
)


class ChatRequest(BaseModel):
    """O que o cliente envia para a API."""

    mensagem: str = Field(
        min_length=1,
        description="Mensagem do cliente.",
        examples=["Meu pedido 1024 já chegou?"],
    )


class ChatResponse(BaseModel):
    """O que a API devolve, já tipado."""

    resposta: str = Field(description="Resposta final do agente.")
    tools_acionadas: list[str] = Field(
        default_factory=list,
        description="Tools que o agente chamou para responder.",
    )
    modelo: str = Field(description="Modelo usado no atendimento.")


@app.get("/", tags=["infra"], summary="Atalho para a documentação")
def raiz() -> dict[str, str]:
    """Atalho para a documentação interativa."""
    return {"docs": "/docs"}


@app.post("/chat", tags=["atendimento"], summary="Atende uma mensagem de cliente")
def chat(requisicao: ChatRequest) -> ChatResponse:
    """Envia a mensagem ao agente e devolve a resposta com as tools usadas."""
    resultado = agente.invoke({"messages": [{"role": "user", "content": requisicao.mensagem}]})
    mensagens = resultado["messages"]

    tools_acionadas = [
        chamada["name"]
        for mensagem in mensagens
        if isinstance(mensagem, AIMessage)
        for chamada in mensagem.tool_calls
    ]

    return ChatResponse(
        resposta=mensagens[-1].text,
        tools_acionadas=tools_acionadas,
        modelo=MODELO,
    )
