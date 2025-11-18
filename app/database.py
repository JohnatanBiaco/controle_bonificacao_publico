import psycopg2
from psycopg2.extras import RealDictCursor
import os

def get_db_connection():
    """Conexão com PostgreSQL LOCAL"""
    conn = psycopg2.connect(
        host="localhost",
        database="bonificacao",
        user="Seu usuario do DB",
        password="Sua senha do DB",
        port="5432",
        cursor_factory=RealDictCursor
    )
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # --- Criar tabela funcionarios se não existir ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS funcionarios (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            funcao TEXT NOT NULL,
            ativo BOOLEAN DEFAULT TRUE,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Garantir coluna funcao existe
    cursor.execute("""
        ALTER TABLE funcionarios
        ADD COLUMN IF NOT EXISTS funcao TEXT;
    """)

    # Garantir coluna ativo
    cursor.execute("""
        ALTER TABLE funcionarios
        ADD COLUMN IF NOT EXISTS ativo BOOLEAN DEFAULT TRUE;
    """)

    # Garantir coluna data_cadastro
    cursor.execute("""
        ALTER TABLE funcionarios
        ADD COLUMN IF NOT EXISTS data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    """)

    # Adicionar constraint CHECK se não existir (PostgreSQL não tem "IF NOT EXISTS" para CHECK)
    cursor.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'funcionarios_funcao_check'
            ) THEN
                ALTER TABLE funcionarios
                ADD CONSTRAINT funcionarios_funcao_check
                CHECK (funcao IN ('LIDER','OPERADOR','AJUDANTE'));
            END IF;
        END;
        $$;
    """)

    # --------------------------
    # OCORRENCIAS
    # --------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ocorrencias (
            id SERIAL PRIMARY KEY,
            funcionario_id INTEGER NOT NULL REFERENCES funcionarios(id),
            tipo TEXT NOT NULL,
            data DATE NOT NULL,
            observacao TEXT,
            anula_ocorrencia_id INTEGER,
            registrado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        ALTER TABLE ocorrencias
        ADD COLUMN IF NOT EXISTS registrado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    """)

    # --------------------------
    # REGRAS BONUS
    # --------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS regras_bonus (
            id SERIAL PRIMARY KEY,
            tipo TEXT UNIQUE NOT NULL,
            categoria TEXT NOT NULL,
            desconto REAL NOT NULL,
            limite INTEGER,
            descricao TEXT
        )
    """)

    # Inserir regras padrão caso não existam
    regras_padrao = [
        ('falta','elimina',100,None,'Perde todo o bônus'),
        ('atestado','limite',100,2,'Mais de 2 atestados perde o bônus'),
        ('advertencia','elimina',100,None,'Perde todo o bônus'),
        ('suspensao','elimina',100,None,'Perde todo o bônus'),
        ('atraso','elimina',100,None,'Perde todo o bônus'),
        ('saida_antecipada','elimina',100,None,'Perde todo o bônus'),
        ('reclamacao_qualidade','percentual',10,None,'Reduz 10% do bônus'),
        ('esqueceu_ponto','percentual',10,None,'Reduz 10% do bônus'),
        ('avaria_menor','percentual',10,None,'Reduz 10% do bônus'),
        ('avaria_grave','percentual',20,None,'Reduz 20% do bônus'),
        ('supermeta_110','bonus',10,1,'Bônus de 10% por supermeta 110%'),
        ('supermeta_120','bonus',20,1,'Bônus de 20% por supermeta 120%')
    ]

    for regra in regras_padrao:
        cursor.execute("""
            INSERT INTO regras_bonus(tipo, categoria, desconto, limite, descricao)
            VALUES (%s,%s,%s,%s,%s)
            ON CONFLICT (tipo) DO NOTHING
        """, regra)

    conn.commit()
    conn.close()
    print("✅ Banco atualizado e sincronizado automaticamente!")
