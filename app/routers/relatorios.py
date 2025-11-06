from fastapi import APIRouter, HTTPException, Query
from app.database import get_db_connection
from app.models import PeriodoRelatorio
from psycopg2.extras import RealDictCursor

router = APIRouter()


def calcular_bonus_funcionario(funcionario_id: str, data_inicio: str, data_fim: str):
    """Calcula o bônus de um funcionário em um período"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Busca funcionário
        cursor.execute("SELECT nome FROM funcionarios WHERE id = %s", (funcionario_id,))
        func = cursor.fetchone()
        if not func:
            return None

        # Busca ocorrências do período, incluindo anulações
        cursor.execute("""
            SELECT 
                o.id,
                o.tipo,
                o.anula_ocorrencia_id,
                o_anulada.tipo as tipo_anulada
            FROM ocorrencias o
            LEFT JOIN ocorrencias o_anulada ON o.anula_ocorrencia_id = o_anulada.id
            WHERE o.funcionario_id = %s AND o.data >= %s AND o.data <= %s
            ORDER BY o.data
        """, (funcionario_id, data_inicio, data_fim))
        ocorrencias_raw = cursor.fetchall()

        # Busca regras de bônus
        cursor.execute("SELECT tipo, categoria, desconto, limite FROM regras_bonus")
        regras = {row['tipo']: {"categoria": row['categoria'], "desconto": row['desconto'], "limite": row['limite']}
                  for row in cursor.fetchall()}

    finally:
        conn.close()

    # Processa ocorrências considerando anulações
    ocorrencias_efetivas = []
    ocorrencias_anuladas = set()

    # Identifica ocorrências que foram anuladas
    for row in ocorrencias_raw:
        if row['anula_ocorrencia_id']:
            ocorrencias_anuladas.add(row['anula_ocorrencia_id'])

    # Processa ocorrências não anuladas
    for row in ocorrencias_raw:
        if row['id'] in ocorrencias_anuladas:
            continue
        if row['anula_ocorrencia_id']:
            ocorrencias_efetivas.append('atestado')
        else:
            ocorrencias_efetivas.append(row['tipo'])

    bonus_final = 100.0
    detalhes = []
    perdeu_bonus = False

    # Conta atestados (que não anulam outras ocorrências)
    qtd_atestados = ocorrencias_efetivas.count('atestado')

    ocorrencias_processadas = set()
    for ocorrencia in ocorrencias_efetivas:
        if ocorrencia in ocorrencias_processadas and regras.get(ocorrencia, {}).get('categoria') != 'percentual':
            continue

        regra = regras.get(ocorrencia)
        if not regra:
            continue

        categoria = regra['categoria']
        desconto = regra['desconto']
        limite = regra.get('limite')

        if categoria == 'elimina':
            perdeu_bonus = True
            detalhes.append({"tipo": ocorrencia, "impacto": "Elimina bônus", "desconto": 100})
        elif categoria == 'limite' and ocorrencia == 'atestado':
            if qtd_atestados > limite:
                perdeu_bonus = True
                detalhes.append({
                    "tipo": ocorrencia,
                    "impacto": f"Excedeu limite de {limite} atestados ({qtd_atestados})",
                    "desconto": 100
                })
        elif categoria == 'percentual' and not perdeu_bonus:
            bonus_final -= desconto
            detalhes.append({"tipo": ocorrencia, "impacto": f"Reduz {desconto}%", "desconto": desconto})

        ocorrencias_processadas.add(ocorrencia)

    if perdeu_bonus:
        bonus_final = 0
    else:
        bonus_final = max(0, bonus_final)

    return {
        "funcionario_id": funcionario_id,
        "nome": func['nome'],
        "bonus_percentual": round(bonus_final, 2),
        "recebe_bonus": bonus_final > 0,
        "total_ocorrencias": len(ocorrencias_efetivas),
        "atestados": qtd_atestados,
        "detalhes": detalhes,
        "ocorrencias_anuladas": len(ocorrencias_anuladas)
    }


@router.get("/regras")
def listar_regras():
    """Lista todas as regras de bonificação"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute("SELECT tipo, categoria, desconto, limite, descricao FROM regras_bonus")
        return cursor.fetchall()
    finally:
        conn.close()


@router.get("/bonus/{funcionario_id}")
def calcular_bonus(
    funcionario_id: str,
    data_inicio: str = Query(..., description="Data início (YYYY-MM-DD)"),
    data_fim: str = Query(..., description="Data fim (YYYY-MM-DD)")
):
    """Calcula o bônus de um funcionário específico"""
    resultado = calcular_bonus_funcionario(funcionario_id, data_inicio, data_fim)
    if not resultado:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return resultado


@router.post("/relatorio/geral")
def relatorio_geral(periodo: PeriodoRelatorio):
    """Gera relatório geral de todos os funcionários ativos"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute("SELECT id FROM funcionarios WHERE ativo = TRUE")
        funcionarios_ids = [row['id'] for row in cursor.fetchall()]
    finally:
        conn.close()

    resultados = [calcular_bonus_funcionario(fid, periodo.data_inicio, periodo.data_fim)
                  for fid in funcionarios_ids if calcular_bonus_funcionario(fid, periodo.data_inicio, periodo.data_fim)]

    return {
        "periodo": {"inicio": periodo.data_inicio, "fim": periodo.data_fim},
        "total_funcionarios": len(resultados),
        "recebem_bonus": sum(1 for r in resultados if r['recebe_bonus']),
        "nao_recebem_bonus": sum(1 for r in resultados if not r['recebe_bonus']),
        "funcionarios": resultados
    }