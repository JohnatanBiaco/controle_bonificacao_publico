# teste_local.py
import psycopg2

print("🧪 Testando PostgreSQL LOCAL...")

try:
    conn = psycopg2.connect(
        host="localhost",
        database="bonificacao",
        user="postgres",
        password="Ybrank2146",  # 👈 SENHA da sua instalação
        port="5432"
    )
    print("🎉 PostgreSQL LOCAL conectado!")
    conn.close()
except Exception as e:
    print(f"❌ Erro: {e}")
    print("💡 Verifique se:")
    print("   - PostgreSQL está instalado")
    print("   - O serviço está rodando")
    print("   - A senha está correta")