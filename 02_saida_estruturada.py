"""Etapa 2 - saída estruturada: o modelo devolve um objeto Pydantic, não texto livre."""

import os
from typing import Literal

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise SystemExit("OPENROUTER_API_KEY não definida. Copie .env.example para .env e preencha a chave.")


class Triagem(BaseModel):
    """Triagem de uma mensagem de cliente."""

    categoria: Literal["pedido", "estoque", "financeiro", "outro"] = Field(
        description="Assunto principal da mensagem."
    )
    urgencia: Literal["baixa", "media", "alta"] = Field(
        description="Prioridade do atendimento."
    )
    resumo: str = Field(description="Resumo da mensagem em uma frase curta.")


modelo = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
    temperature=0,
)

triador = modelo.with_structured_output(Triagem)

mensagem = (
    "Comprei o pedido 1024 há 10 dias e ainda não chegou. "
    "Preciso do produto para o casamento da minha irmã no sábado, é urgente!"
)

triagem = triador.invoke(mensagem)

print(type(triagem).__name__)
print(triagem.model_dump_json(indent=2))
