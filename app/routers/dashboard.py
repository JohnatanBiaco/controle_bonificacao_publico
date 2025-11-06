from fastapi import APIRouter
from app.database import get_db_connection
from datetime import date

router = APIRouter()

@router.get("/dashboard")
def dashboard_resumo():
    """Retorna estatísticas para o dashboard"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Total de funcionários ativos
    cursor.execute("SELECT COUNT(*) AS total FROM funcionarios WHERE ativo = TRUE")
    total_func = cursor.fetchone()['total']

    # Ocorrências do mês atual
    hoje = date.today()
    primeiro_dia = hoje.replace(day=1)
    cursor.execute("SELECT COUNT(*) AS total FROM ocorrencias WHERE data >= %s", (primeiro_dia,))
    ocorrencias_mes = cursor.fetchone()['total']

    # Ocorrências por tipo no mês
    cursor.execute("""
        SELECT tipo, COUNT(*) AS qtd
        FROM ocorrencias
        WHERE data >= %s
        GROUP BY tipo
        ORDER BY qtd DESC
    """, (primeiro_dia,))
    ocorrencias_por_tipo = cursor.fetchall()

    conn.close()

    return {
        "total_funcionarios": total_func,
        "ocorrencias_mes_atual": ocorrencias_mes,
        "ocorrencias_por_tipo": ocorrencias_por_tipo
    }
