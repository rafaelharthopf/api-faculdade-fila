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
        fila.insert(0, cliente) 
    else:
        fila.append(cliente)  

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

    cliente_atendido = fila[0]
    
    cliente_atendido.atendido = True
    
    fila.append(cliente_atendido)
    
    fila.pop(0)  

    if not fila:
        return {"message": "Todos os clientes foram atendidos."}
    
    if fila[0].atendido:
        return {"message": "Todos os clientes foram atendidos."}


    for index, cliente in enumerate(fila):
        cliente.id = index + 1 

    return {"message": f"{cliente_atendido.nome} foi atendido.", "next_cliente": fila[0].nome}




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
