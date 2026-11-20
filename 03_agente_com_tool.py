"""Etapa 3 - agente com tools: o modelo decide quando consultar os dados."""

import json
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise SystemExit("OPENROUTER_API_KEY não definida. Copie .env.example para .env e preencha a chave.")

# Dados mockados: em produção seriam um banco ou uma API interna.
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
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
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

if __name__ == "__main__":
    pergunta = "Meu pedido 1024 já chegou? E vocês têm mouse gamer em estoque?"
    print(f"\nPergunta: {pergunta}\n")

    resultado = agente.invoke({"messages": [{"role": "user", "content": pergunta}]})

    for mensagem in resultado["messages"]:
        if mensagem.type == "ai" and mensagem.tool_calls:
            for chamada in mensagem.tool_calls:
                print(f"-> tool {chamada['name']}({chamada['args']})")
        elif mensagem.type == "tool":
            print(f"<- retorno {mensagem.name}: {mensagem.content}")

    print(f"\nResposta: {resultado['messages'][-1].text}")
