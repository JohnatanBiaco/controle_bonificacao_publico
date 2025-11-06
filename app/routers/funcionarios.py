from fastapi import APIRouter, HTTPException
from app.database import get_db_connection
from app.models import Funcionario, FuncionarioUpdate
from psycopg2.extras import RealDictCursor

router = APIRouter()

@router.post("/funcionarios")
def criar_funcionario(funcionario: Funcionario):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verifica se funcionário já existe
        cursor.execute("SELECT id FROM funcionarios WHERE id = %s", (funcionario.id,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Funcionário com este ID já existe")
            
        cursor.execute(
            "INSERT INTO funcionarios (id, nome, funcao) VALUES (%s, %s, %s)",
            (funcionario.id, funcionario.nome, funcionario.funcao)
        )
        conn.commit()
        return {"message": "Funcionário cadastrado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao cadastrar funcionário: {str(e)}")
    finally:
        conn.close()

@router.get("/funcionarios")
def listar_funcionarios(ativo: bool = True):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
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
    cursor = conn.cursor(cursor_factory=RealDictCursor)
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
    
    try:
        cursor.execute(query, values)
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Funcionário não encontrado")
        conn.commit()
        return {"message": "Funcionário atualizado com sucesso"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar funcionário: {str(e)}")
    finally:
        conn.close()

@router.delete("/funcionarios/{funcionario_id}")
def excluir_funcionario(funcionario_id: str):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Verifica se o funcionário existe
        cursor.execute("SELECT id FROM funcionarios WHERE id = %s", (funcionario_id,))
        resultado = cursor.fetchone()
        
        if not resultado:
            raise HTTPException(status_code=404, detail="Funcionário não encontrado")

        # Verifica se o funcionário tem ocorrências
        cursor.execute("SELECT COUNT(*) as count FROM ocorrencias WHERE funcionario_id = %s", (funcionario_id,))
        result_count = cursor.fetchone()
        
        count_ocorrencias = result_count['count'] if result_count else 0
        
        if count_ocorrencias > 0:
            # Se tiver ocorrências, apenas desativa
            cursor_normal = conn.cursor()
            cursor_normal.execute("UPDATE funcionarios SET ativo = FALSE WHERE id = %s", (funcionario_id,))
            conn.commit()
            return {"message": "Funcionário desativado (possui ocorrências vinculadas)"}
        else:
            # Se não tiver ocorrências, pode excluir
            cursor_normal = conn.cursor()
            cursor_normal.execute("DELETE FROM funcionarios WHERE id = %s", (funcionario_id,))
            conn.commit()
            return {"message": "Funcionário excluído com sucesso"}
            
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao excluir funcionário: {str(e)}")
    finally:
        conn.close()