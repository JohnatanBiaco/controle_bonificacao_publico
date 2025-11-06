import psycopg2
from psycopg2.extras import RealDictCursor
import os

def get_db_connection():
    """Conexão com PostgreSQL LOCAL"""
    conn = psycopg2.connect(
        host="localhost",
        database="bonificacao",
        user="postgres",
        password="Ybrank2146",
        port="5432",
        cursor_factory=RealDictCursor
    )
    return conn

def init_db():
    """Inicializa o banco de dados PostgreSQL LOCAL"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS funcionarios (
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            funcao TEXT,
            ativo BOOLEAN DEFAULT true,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ocorrencias (
            id SERIAL PRIMARY KEY,
            funcionario_id TEXT NOT NULL,
            tipo TEXT NOT NULL,
            data DATE NOT NULL,
            observacao TEXT,
            anula_ocorrencia_id INTEGER,
            registrado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id)
        )
    """)
    
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
    
    regras_padrao = [
        ('falta', 'elimina', 100, None, 'Perde todo o bônus'),
        ('atestado', 'limite', 100, 2, 'Mais de 2 atestados perde o bônus'),
        ('advertencia', 'elimina', 100, None, 'Perde todo o bônus'),
        ('suspensao', 'elimina', 100, None, 'Perde todo o bônus'),
        ('atraso', 'elimina', 100, None, 'Perde todo o bônus'),
        ('saida_antecipada', 'elimina', 100, None, 'Perde todo o bônus'),
        ('reclamacao_qualidade', 'percentual', 10, None, 'Reduz 10% do bônus'),
        ('esqueceu_ponto', 'percentual', 10, None, 'Reduz 10% do bônus'),
        ('avaria_menor', 'percentual', 10, None, 'Reduz 10% do bônus'),
        ('avaria_grave', 'percentual', 20, None, 'Reduz 20% do bônus')
    ]
    
    for regra in regras_padrao:
        cursor.execute("""
            INSERT INTO regras_bonus (tipo, categoria, desconto, limite, descricao)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (tipo) DO NOTHING
        """, regra)
    
    conn.commit()
    conn.close()
    print("✅ Banco PostgreSQL LOCAL criado com sucesso!")
