from fastapi import APIRouter, HTTPException
from typing import Optional
from app.database import get_db_connection
from app.models import Ocorrencia
from psycopg2.extras import RealDictCursor

router = APIRouter()


@router.post("/ocorrencias")
def registrar_ocorrencia(ocorrencia: Ocorrencia):
    """Registra uma nova ocorrência"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Verifica se funcionário existe
        cursor.execute("SELECT 1 FROM funcionarios WHERE id = %s", (ocorrencia.funcionario_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Funcionário não encontrado")

        # Verifica se tipo é válido
        cursor.execute("SELECT 1 FROM regras_bonus WHERE tipo = %s", (ocorrencia.tipo,))
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail="Tipo de ocorrência inválido")

        # Se for um atestado que anula uma ocorrência, verifica se a ocorrência existe
        if ocorrencia.anula_ocorrencia_id:
            cursor.execute("""
                SELECT 1 FROM ocorrencias 
                WHERE id = %s AND funcionario_id = %s AND tipo IN ('falta', 'atraso', 'saida_antecipada')
            """, (ocorrencia.anula_ocorrencia_id, ocorrencia.funcionario_id))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=400,
                    detail="Ocorrência a ser anulada não encontrada ou tipo inválido para anulação"
                )

        cursor.execute("""
            INSERT INTO ocorrencias (funcionario_id, tipo, data, observacao, anula_ocorrencia_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            ocorrencia.funcionario_id,
            ocorrencia.tipo,
            ocorrencia.data,
            ocorrencia.observacao,
            ocorrencia.anula_ocorrencia_id
        ))

        ocorrencia_id = cursor.fetchone()['id']
        conn.commit()

        return {"message": "Ocorrência registrada com sucesso", "id": ocorrencia_id}

    finally:
        conn.close()


@router.get("/ocorrencias")
def listar_ocorrencias(
    funcionario_id: Optional[str] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    tipo: Optional[str] = None
):
    """Lista ocorrências com filtros opcionais"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT 
            o.id, 
            o.funcionario_id, 
            f.nome, 
            o.tipo, 
            o.data, 
            o.observacao, 
            o.anula_ocorrencia_id,
            o.registrado_em,
            o_anulada.tipo as tipo_anulada,
            o_anulada.data as data_anulada
        FROM ocorrencias o
        JOIN funcionarios f ON o.funcionario_id = f.id
        LEFT JOIN ocorrencias o_anulada ON o.anula_ocorrencia_id = o_anulada.id
        WHERE 1=1
    """
    params = []

    if funcionario_id:
        query += " AND o.funcionario_id = %s"
        params.append(funcionario_id)
    if data_inicio:
        query += " AND o.data >= %s"
        params.append(data_inicio)
    if data_fim:
        query += " AND o.data <= %s"
        params.append(data_fim)
    if tipo:
        query += " AND o.tipo = %s"
        params.append(tipo)

    query += " ORDER BY o.data DESC, o.registrado_em DESC"

    cursor.execute(query, params)
    ocorrencias = []

    for row in cursor.fetchall():
        ocorrencia = dict(row)
        if row['anula_ocorrencia_id']:
            ocorrencia["ocorrencia_anulada"] = {
                "tipo": row['tipo_anulada'],
                "data": row['data_anulada']
            }
        ocorrencias.append(ocorrencia)

    conn.close()
    return ocorrencias


@router.get("/ocorrencias/{funcionario_id}/pendentes")
def listar_ocorrencias_pendentes_anulacao(funcionario_id: str):
    """Lista ocorrências que podem ser anuladas por atestado (falta, atraso, saida_antecipada)"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT o.id, o.tipo, o.data, o.observacao
        FROM ocorrencias o
        WHERE o.funcionario_id = %s
        AND o.tipo IN ('falta', 'atraso', 'saida_antecipada')
        AND o.id NOT IN (
            SELECT anula_ocorrencia_id 
            FROM ocorrencias 
            WHERE anula_ocorrencia_id IS NOT NULL
        )
        ORDER BY o.data DESC
    """, (funcionario_id,))

    pendentes = cursor.fetchall()
    conn.close()
    return pendentes


@router.delete("/ocorrencias/{ocorrencia_id}")
def deletar_ocorrencia(ocorrencia_id: int):
    """Deleta uma ocorrência"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Verifica se a ocorrência está sendo usada em algum atestado
        cursor.execute("SELECT 1 FROM ocorrencias WHERE anula_ocorrencia_id = %s", (ocorrencia_id,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="Não é possível deletar esta ocorrência pois ela está vinculada a um atestado"
            )

        cursor.execute("DELETE FROM ocorrencias WHERE id = %s", (ocorrencia_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Ocorrência não encontrada")
        conn.commit()
        return {"message": "Ocorrência deletada com sucesso"}

    finally:
        conn.close()
