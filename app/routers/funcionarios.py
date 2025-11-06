from fastapi import APIRouter, HTTPException
from app.database import get_db_connection
from app.models import Funcionario, FuncionarioUpdate

router = APIRouter()

@router.post("/funcionarios")
def criar_funcionario(funcionario: Funcionario):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO funcionarios (id, nome, funcao) VALUES (%s, %s, %s)",
        (funcionario.id, funcionario.nome, funcionario.funcao)
    )
    conn.commit()
    conn.close()
    return {"message": "Funcionário cadastrado com sucesso"}

@router.get("/funcionarios")
def listar_funcionarios(ativo: bool = True):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nome, funcao, ativo, data_cadastro FROM funcionarios WHERE ativo=%s ORDER BY nome",
        (ativo,)
    )
    funcionarios = cursor.fetchall()
    conn.close()
    return funcionarios

@router.get("/funcionarios/{funcionario_id}")
def obter_funcionario(funcionario_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nome, funcao, ativo, data_cadastro FROM funcionarios WHERE id=%s",
        (funcionario_id,)
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return row

@router.put("/funcionarios/{funcionario_id}")
def atualizar_funcionario(funcionario_id: str, dados: FuncionarioUpdate):
    updates = []
    values = []

    if dados.nome is not None:
        updates.append("nome=%s")
        values.append(dados.nome)
    if dados.funcao is not None:
        updates.append("funcao=%s")
        values.append(dados.funcao)
    if dados.ativo is not None:
        updates.append("ativo=%s")
        values.append(dados.ativo)

    if not updates:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")

    values.append(funcionario_id)
    query = f"UPDATE funcionarios SET {', '.join(updates)} WHERE id=%s"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, values)
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    conn.commit()
    conn.close()
    return {"message": "Funcionário atualizado com sucesso"}
