# main.py
import sys
import os
import logging

# CONFIGURAÇÃO CRÍTICA - deve vir antes de qualquer import
if getattr(sys, 'frozen', False):
    # Modo executável - configura logging simples
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

# Configura caminhos
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Adiciona ao path para imports
sys.path.insert(0, BASE_DIR)


# Agora importa as bibliotecas
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Sistema de Bonificação")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_missing_directories():
    """Cria diretórios necessários se não existirem"""
    directories = [
        os.path.join(BASE_DIR, "static", "css"),
        os.path.join(BASE_DIR, "static", "js"),
        os.path.join(BASE_DIR, "app", "templates"),
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Criado diretório: {directory}")

def create_default_files():
    """Cria arquivos padrão se não existirem"""
    
    # CSS padrão
    css_content = """* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
}
.container {
    max-width: 1400px;
    margin: 0 auto;
}
h1 {
    color: white;
    text-align: center;
    margin-bottom: 30px;
    font-size: 2.5em;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}"""
    
    css_path = os.path.join(BASE_DIR, "static", "css", "style.css")
    if not os.path.exists(css_path):
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(css_content)
        print("✅ Arquivo CSS criado")

    # JS padrão mínimo
    js_content = """console.log('Sistema de Bonificação carregado');
// Funções básicas do sistema
function showTab(tabName) {
    console.log('Mudando para aba:', tabName);
    alert('Sistema carregado! Acesse /docs para a API completa.');
}"""
    
    js_path = os.path.join(BASE_DIR, "static", "js", "app.js")
    if not os.path.exists(js_path):
        with open(js_path, "w", encoding="utf-8") as f:
            f.write(js_content)
        print("✅ Arquivo JS criado")

# Configura arquivos estáticos de forma segura
create_missing_directories()
create_default_files()

static_dir = os.path.join(BASE_DIR, "static")
templates_dir = os.path.join(BASE_DIR, "app", "templates")

try:
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        print("✅ Arquivos estáticos carregados")
    else:
        print("⚠️  Pasta static não encontrada, criando...")
        os.makedirs(static_dir, exist_ok=True)
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        
except Exception as e:
    print(f"⚠️  Erro ao carregar arquivos estáticos: {e}")

# Importa e configura as rotas - COM TRATAMENTO MELHORADO
try:
    # Tenta importar os routers
    from app.routers import funcionarios, ocorrencias, relatorios, dashboard
    from app.database import init_db
    
    # Inicializa o banco
    init_db()
    
    # Adiciona as rotas
    app.include_router(funcionarios.router, prefix="/api", tags=["Funcionários"])
    app.include_router(ocorrencias.router, prefix="/api", tags=["Ocorrências"])
    app.include_router(relatorios.router, prefix="/api", tags=["Relatórios"])
    app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
    
    print("✅ Rotas da API carregadas")
    
except ImportError as e:
    print(f"⚠️  Módulos não encontrados (execução básica): {e}")
    print("⚠️  A API não estará disponível, apenas a interface web")
except Exception as e:
    print(f"❌ Erro ao carregar rotas: {e}")

# HTML completo para fallback
COMPLETE_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Bonificação</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 {
            color: #667eea;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .alert-success {
            background: #d3f9d8;
            color: #2f9e44;
            border: 1px solid #b2f2bb;
        }
        .alert-warning {
            background: #fff3bf;
            color: #e67700;
            border: 1px solid #ffec99;
        }
        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            border: 1px solid #e9ecef;
        }
        .card h3 {
            color: #495057;
            margin-bottom: 10px;
        }
        .btn {
            display: inline-block;
            padding: 12px 24px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            margin: 5px;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #5568d3;
        }
        .api-links {
            margin-top: 30px;
        }
        .api-links h2 {
            color: #495057;
            margin-bottom: 15px;
        }
        .api-links ul {
            list-style: none;
        }
        .api-links li {
            margin: 10px 0;
        }
        .api-links a {
            color: #667eea;
            text-decoration: none;
        }
        .api-links a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Sistema de Bonificação</h1>
        
        <div class="alert alert-success">
            ✅ <strong>Servidor está funcionando!</strong> O sistema foi iniciado com sucesso.
        </div>
        
        <div class="alert alert-warning">
            ⚠️ <strong>Arquivos estáticos não carregados</strong>, mas toda a funcionalidade da API está disponível.
        </div>

        <div class="cards">
            <div class="card">
                <h3>📚 Documentação</h3>
                <p>API completa com Swagger UI</p>
                <a href="/docs" class="btn" target="_blank">Acessar Docs</a>
            </div>
            <div class="card">
                <h3>👥 Funcionários</h3>
                <p>Gerenciar funcionários</p>
                <a href="/api/funcionarios" class="btn" target="_blank">Ver API</a>
            </div>
            <div class="card">
                <h3>📋 Ocorrências</h3>
                <p>Registrar ocorrências</p>
                <a href="/api/ocorrencias" class="btn" target="_blank">Ver API</a>
            </div>
        </div>

        <div class="api-links">
            <h2>🔗 Endpoints da API</h2>
            <ul>
                <li><a href="/api/funcionarios" target="_blank"><strong>GET /api/funcionarios</strong> - Listar funcionários</a></li>
                <li><a href="/api/ocorrencias" target="_blank"><strong>GET /api/ocorrencias</strong> - Listar ocorrências</a></li>
                <li><a href="/api/dashboard" target="_blank"><strong>GET /api/dashboard</strong> - Dashboard</a></li>
                <li><a href="/api/regras" target="_blank"><strong>GET /api/regras</strong> - Regras de bonificação</a></li>
            </ul>
        </div>

        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6;">
            <p><strong>💡 Dica:</strong> Use a documentação interativa em <a href="/docs" style="color: #667eea;">/docs</a> para testar todas as funcionalidades da API.</p>
        </div>
    </div>

    <script>
        console.log('Sistema de Bonificação - Interface Fallback');
        // Funções básicas para navegação
        function showTab(tabName) {
            alert('Sistema funcionando! Acesse a documentação em /docs para API completa.');
        }
    </script>
</body>
</html>
"""

# Página principal
@app.get("/", response_class=HTMLResponse)
async def home():
    template_paths = [
        os.path.join(templates_dir, "index.html"),
        os.path.join(BASE_DIR, "app", "templates", "index.html"),
        os.path.join(BASE_DIR, "templates", "index.html")
    ]
    
    for template_path in template_paths:
        if os.path.exists(template_path):
            try:
                with open(template_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                print(f"Erro ao ler template {template_path}: {e}")
                continue
    
    # Retorna HTML completo como fallback
    return COMPLETE_HTML

def main():
    import uvicorn
    
    print("\n" + "="*50)
    print("🚀 SISTEMA DE BONIFICAÇÃO INICIADO")
    print("="*50)
    print("📍 URL: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("⏹️  Pressione Ctrl+C para parar")
    print("="*50)
    
    # Configuração do Uvicorn para executável
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()