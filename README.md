🎯 Sistema de Bonificação – FastAPI + PostgreSQL

Um sistema completo para gestão de funcionários, registro de ocorrências e cálculo automático de bonificação, desenvolvido com FastAPI e PostgreSQL.  
Ideal para uso interno em empresas, setor operacional, RH ou gestão de desempenho.

---

## 🛠️ Tecnologias utilizadas

- Python 3.13
- FastAPI
- Uvicorn
- PostgreSQL
- psycopg2
- Pydantic
- HTML + CSS + JavaScript
- PyInstaller (opcional)
- Inno Setup (opcional)

---

## 📦 Funcionalidades

### 👥 Gestão de Funcionários
- Cadastro
- Atualização
- Desativação automática se houver ocorrências vinculadas
- Listagem com filtro por status (ativo/inativo)

### 📝 Registro de Ocorrências
Tipos já configurados:
- Falta
- Atraso
- Saída antecipada
- Atestado (com anulação de ocorrências)
- Advertência
- Suspensão
- Reclamação de qualidade
- Avaria (leve e grave)
- Supermetas (110% e 120%)

### 🎁 Regras Automáticas de Bonificação
- Regras percentuais
- Regras de eliminação total
- Regras com limite de uso
- Configuração dinâmica

### 📊 Dashboard
- Ocorrências por tipo
- Funcionários ativos
- Indicadores resumo
- Dados consolidados

### 📄 Relatórios
- Filtragem por período
- Filtragem por funcionário
- Filtragem por tipo
- Exibição estruturada

---

## ⚙️ Requisitos

- Python 3.10+
- PostgreSQL 12+
- pip instalado

---

## 🗄️ Configurando o Banco de Dados

1. Instale PostgreSQL.
2. Crie um banco chamado:

bonificacao

3. Configure seu PostgreSQL com as credenciais usadas no projeto (database.py):

user: --  
password: --  
host: localhost 
port: 5432

4. Ao iniciar o sistema, as tabelas serão criadas automaticamente via init_db().

---

## 💻 Como executar o servidor

### 1. Crie o ambiente virtual

python -m venv venv

### 2. Ative o ambiente

Windows:
venv\Scripts\activate

Linux/Mac:
source venv/bin/activate

### 3. Instale as dependências

pip install -r requirements.txt

### 4. Execute o servidor

uvicorn main:app --reload

Acesse no navegador:

Interface: http://127.0.0.1:8000  
Documentação (Swagger): http://127.0.0.1:8000/docs

---

## 👤 Autor

Johnatan Luis Biaco  
Estudante de Sistemas de Informação • Desenvolvedor Python
