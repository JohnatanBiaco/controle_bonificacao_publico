from fastapi import APIRouter, HTTPException
from app.database import get_db_connection
from app.models import Funcionario, FuncionarioUpdate, FuncaoEnumFuncionario
from psycopg2.extras import RealDictCursor

router = APIRouter()

@router.post("/funcionarios")
def criar_funcionario(funcionario: Funcionario):
    print("📥 RECEBIDO NO BACKEND:", funcionario)
    print("📥 TIPO DO OBJETO:", type(funcionario))
    print("📥 FUNCAO:", funcionario.funcao)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # ⬇️ AQUI É A LINHA CORRETA — usa .name que SEMPRE retorna 'LIDER'
        cursor.execute(
            "INSERT INTO funcionarios (nome, funcao) VALUES (%s, %s) RETURNING id",
            (funcionario.nome, funcionario.funcao.name)
        )

        result = cursor.fetchone()
        print("📌 RESULTADO DO FETCH:", result)

        if not result:
            raise Exception("INSERT não retornou id — possível erro de CHECK ou coluna inválida")

        novo_id = result[0] if isinstance(result, tuple) else result["id"]

        conn.commit()
        return {"message": "Funcionário cadastrado com sucesso", "id": novo_id}

    except Exception as e:
        conn.rollback()
        print("🔥 ERRO REAL NO /funcionarios:", repr(e))
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
def obter_funcionario(funcionario_id: int):
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
def atualizar_funcionario(funcionario_id: int, dados: FuncionarioUpdate):
    updates = []
    values = []

    if dados.nome is not None:
        updates.append("nome=%s")
        values.append(dados.nome)

    if dados.funcao is not None:
        updates.append("funcao=%s")
        values.append(dados.funcao.name)  # ⬅️ Corrigido aqui também

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
        print("🔥 ERRO REAL AO ATUALIZAR FUNCIONARIO:", repr(e))
        raise HTTPException(status_code=500, detail="Erro ao atualizar funcionário")

    finally:
        conn.close()


@router.delete("/funcionarios/{funcionario_id}")
def excluir_funcionario(funcionario_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Verifica se funcionário existe
        cursor.execute("SELECT id FROM funcionarios WHERE id = %s", (funcionario_id,))
        resultado = cursor.fetchone()

        if not resultado:
            raise HTTPException(status_code=404, detail="Funcionário não encontrado")

        # Conta ocorrências
        cursor.execute("SELECT COUNT(*) as count FROM ocorrencias WHERE funcionario_id = %s", (funcionario_id,))
        result_count = cursor.fetchone()
        count_ocorrencias = result_count['count'] if result_count else 0

        # Se tiver ocorrências → desativa
        if count_ocorrencias > 0:
            cursor2 = conn.cursor()
            cursor2.execute("UPDATE funcionarios SET ativo = FALSE WHERE id = %s", (funcionario_id,))
            conn.commit()
            return {"message": "Funcionário desativado (possui ocorrências vinculadas)"}

        # Se não tiver → exclui
        cursor2 = conn.cursor()
        cursor2.execute("DELETE FROM funcionarios WHERE id = %s", (funcionario_id,))
        conn.commit()
        return {"message": "Funcionário excluído com sucesso"}

    except HTTPException:
        raise

    except Exception as e:
        conn.rollback()
        print("🔥 ERRO REAL NO DELETE FUNCIONARIO:", repr(e))
        raise HTTPException(status_code=500, detail=f"Erro ao excluir funcionário: {str(e)}")

    finally:
        conn.close()
