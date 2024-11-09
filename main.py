from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr, field_validator
from typing import List
from datetime import datetime
import random

app = FastAPI()

class Cliente(BaseModel):
    id: int = None
    nome: constr(max_length=20)
    data_chegada: datetime = None
    atendido: bool = False
    tipo_atendimento: str

    @field_validator('tipo_atendimento')
    @classmethod
    def validar_tipo_atendimento(cls, v):
        if v not in ('N', 'P'):
            raise ValueError('O tipo de atendimento deve ser "N" (normal) ou "P" (prioritário).')
        return v

fila: List[Cliente] = []

def adicionar_cliente_fila(cliente: Cliente):
    cliente.id = len(fila) + 1
    cliente.data_chegada = datetime.now()

    if cliente.tipo_atendimento == 'P':
        posicao_prioritario = -1
        for i in range(len(fila)):
            if fila[i].tipo_atendimento == 'P' and not fila[i].atendido:
                posicao_prioritario = i

        if posicao_prioritario >= 0: 
            fila.insert(posicao_prioritario + 1, cliente)
        else:
            fila.insert(0, cliente)
    else:
        posicao_normal = -1
        for i in range(len(fila)):
            if fila[i].tipo_atendimento == 'N' and not fila[i].atendido:
                posicao_normal = i

        if posicao_normal >= 0:
            fila.insert(posicao_normal + 1, cliente)
        else:
            fila.append(cliente)

    for index, cliente in enumerate(fila):
        cliente.id = index + 1

def reorganizar_fila():
    """ Move clientes atendidos para o final da fila, preservando a ordem. """
    nao_atendidos = [cliente for cliente in fila if not cliente.atendido]
    atendidos = [cliente for cliente in fila if cliente.atendido]
    fila.clear()
    fila.extend(nao_atendidos + atendidos)

@app.post("/fila", response_model=Cliente)
def adicionar_cliente(cliente: Cliente):
    adicionar_cliente_fila(cliente)
    return cliente

@app.get("/fila", response_model=List[Cliente])
def listar_fila():
    return fila

@app.get("/fila/{id}", response_model=Cliente)
def obter_cliente(id: int):
    for cliente in fila:
        if cliente.id == id:
            return cliente
    raise HTTPException(status_code=404, detail="Cliente não encontrado")

@app.put("/fila")
def atualizar_fila():
    if not fila:
        return {"message": "Fila está vazia."}

    for cliente in fila:
        if not cliente.atendido:
            cliente.atendido = True
            reorganizar_fila()
            return {
                "message": f"{cliente.nome} foi atendido.",
                "next_cliente": fila[0].nome if not fila[0].atendido else "Nenhum"
            }

    return {"message": "Todos os clientes foram atendidos."}

@app.delete("/fila/{id}")
def remover_cliente(id: int):
    global fila
    for cliente in fila:
        if cliente.id == id:
            fila = [c for c in fila if c.id != id]
            for index, c in enumerate(fila):
                c.id = index + 1
            return {"message": "Cliente removido da fila."}
    raise HTTPException(status_code=404, detail="Cliente não encontrado")

@app.get("/populate")
def popular_fila():
    nomes = ["João Silva", "Maria Oliveira", "Carlos Souza", "Ana Santos", "Ricardo Almeida",
             "Fernanda Lima", "José Ferreira", "Patrícia Costa", "Lucas Mendes", "Mariana Rocha"]

    for _ in range(5):
        nome = random.choice(nomes)
        tipo_atendimento = random.choice(['N', 'P'])
        cliente = Cliente(nome=nome, tipo_atendimento=tipo_atendimento)
        adicionar_cliente_fila(cliente)

    return {"message": "Fila populada com dados fictícios."}
