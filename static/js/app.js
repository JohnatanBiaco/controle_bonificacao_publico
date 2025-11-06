// Configuração da data de hoje
const hoje = new Date().toISOString().split('T')[0];
document.getElementById('ocorrenciaData').value = hoje;

// Variável global para ocorrências pendentes
let ocorrenciasPendentes = [];

// Funções de navegação
function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(`tab-${tabName}`).classList.add('active');
    event.target.classList.add('active');

    if (tabName === 'funcionarios') carregarFuncionarios();
    if (tabName === 'ocorrencias') carregarOcorrencias();
    if (tabName === 'regras') carregarRegras();
}

// Alertas
function mostrarAlerta(mensagem, tipo = 'success') {
    const container = document.getElementById('alertContainer');
    container.innerHTML = `<div class="alert alert-${tipo}">${mensagem}</div>`;
    setTimeout(() => container.innerHTML = '', 5000);
}

// Dashboard
async function carregarDashboard() {
    try {
        const res = await fetch('/api/dashboard');
        const data = await res.json();
        
        document.getElementById('totalFuncionarios').textContent = data.total_funcionarios;
        document.getElementById('ocorrenciasMes').textContent = data.ocorrencias_mes_atual;
        
        if (data.ocorrencias_por_tipo.length > 0) {
            document.getElementById('tipoMaisComum').textContent = 
                data.ocorrencias_por_tipo[0].tipo.replace('_', ' ');
        } else {
            document.getElementById('tipoMaisComum').textContent = 'Nenhuma';
        }
    } catch (error) {
        console.error('Erro ao carregar dashboard:', error);
    }
}

// Funcionários
async function cadastrarFuncionario(e) {
    e.preventDefault();
    
    const dados = {
        id: document.getElementById('id').value,
        nome: document.getElementById('nome').value,
        funcao: document.getElementById('funcao').value
    };

    try {
        const res = await fetch('/api/funcionarios', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(dados)
        });

        if (res.ok) {
            mostrarAlerta('Funcionário cadastrado com sucesso!');
            document.getElementById('formFuncionario').reset();
            carregarFuncionarios();
            carregarDashboard();
        } else {
            const erro = await res.json();
            mostrarAlerta(erro.detail, 'error');
        }
    } catch (error) {
        mostrarAlerta('Erro ao cadastrar funcionário', 'error');
    }
}

async function carregarFuncionarios() {
    try {
        const res = await fetch('/api/funcionarios');
        const funcionarios = await res.json();
        
        if (funcionarios.length === 0) {
            document.getElementById('listaFuncionarios').innerHTML = 
                '<p style="text-align:center;color:#666;">Nenhum funcionário cadastrado</p>';
            return;
        }

        let html = '<table><thead><tr><th>ID</th><th>Nome</th><th>Função</th></tr></thead><tbody>';
        
        funcionarios.forEach(f => {
            html += `<tr>
                <td>${f.id}</td>
                <td>${f.nome}</td>
                <td>${f.funcao || '-'}</td>
            </tr>`;
        });
        
        html += '</tbody></table>';
        document.getElementById('listaFuncionarios').innerHTML = html;

        // Atualiza select de ocorrências
        const select = document.getElementById('funcionario_id');
        select.innerHTML = '<option value="">Selecione...</option>';
        funcionarios.forEach(f => {
            select.innerHTML += `<option value="${f.id}">${f.nome} (${f.id})</option>`;
        });

    } catch (error) {
        document.getElementById('listaFuncionarios').innerHTML = 
            '<p style="color:red;">Erro ao carregar funcionários</p>';
    }
}

// Função para carregar ocorrências pendentes quando selecionar um funcionário
async function carregarOcorrenciasPendentes(funcionarioId) {
    if (!funcionarioId) {
        document.getElementById('ocorrenciaAnula').innerHTML = '<option value="">Nenhuma ocorrência para anular</option>';
        return;
    }

    try {
        const res = await fetch(`/api/ocorrencias/${funcionarioId}/pendentes`);
        ocorrenciasPendentes = await res.json();
        
        const select = document.getElementById('ocorrenciaAnula');
        select.innerHTML = '<option value="">Não anular nenhuma ocorrência</option>';
        
        if (ocorrenciasPendentes.length === 0) {
            select.innerHTML += '<option value="">Nenhuma ocorrência pendente para anular</option>';
        } else {
            ocorrenciasPendentes.forEach(oc => {
                const dataFormatada = oc.data.split('-').reverse().join('/');
                select.innerHTML += `<option value="${oc.id}">${oc.tipo} - ${dataFormatada} - ${oc.observacao || 'Sem observação'}</option>`;
            });
        }
    } catch (error) {
        console.error('Erro ao carregar ocorrências pendentes:', error);
    }
}

// Ocorrências
async function registrarOcorrencia(e) {
    e.preventDefault();
    
    const anulaOcorrenciaId = document.getElementById('ocorrenciaAnula').value;
    
    const dados = {
        funcionario_id: document.getElementById('funcionario_id').value,
        tipo: document.getElementById('ocorrenciaTipo').value,
        data: document.getElementById('ocorrenciaData').value,
        observacao: document.getElementById('ocorrenciaObs').value,
        anula_ocorrencia_id: anulaOcorrenciaId || null
    };

    try {
        const res = await fetch('/api/ocorrencias', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(dados)
        });

        if (res.ok) {
            let mensagem = 'Ocorrência registrada com sucesso!';
            if (anulaOcorrenciaId) {
                mensagem += ' Ocorrência anulada.';
            }
            
            mostrarAlerta(mensagem);
            document.getElementById('formOcorrencia').reset();
            document.getElementById('ocorrenciaData').value = hoje;
            document.getElementById('ocorrenciaAnula').innerHTML = '<option value="">Não anular nenhuma ocorrência</option>';
            carregarOcorrencias();
            carregarDashboard();
        } else {
            const erro = await res.json();
            mostrarAlerta(erro.detail, 'error');
        }
    } catch (error) {
        mostrarAlerta('Erro ao registrar ocorrência', 'error');
    }
}

async function carregarOcorrencias() {
    try {
        const res = await fetch('/api/ocorrencias');
        const ocorrencias = await res.json();
        
        if (ocorrencias.length === 0) {
            document.getElementById('listaOcorrencias').innerHTML = 
                '<p style="text-align:center;color:#666;">Nenhuma ocorrência registrada</p>';
            return;
        }

        let html = '<table><thead><tr><th>Data</th><th>Funcionário</th><th>Tipo</th><th>Observação</th><th>Anulação</th><th>Ação</th></tr></thead><tbody>';
        
        ocorrencias.slice(0, 50).forEach(o => {
            let anulacaoInfo = '-';
            if (o.anula_ocorrencia_id && o.ocorrencia_anulada) {
                const dataAnulada = o.ocorrencia_anulada.data.split('-').reverse().join('/');
                anulacaoInfo = `<span style="color: #51cf66;" title="Anulou ${o.ocorrencia_anulada.tipo} de ${dataAnulada}">✓ Anulou ${o.ocorrencia_anulada.tipo}</span>`;
            } else if (o.anula_ocorrencia_id) {
                anulacaoInfo = `<span style="color: #51cf66;">✓ Anulou ocorrência #${o.anula_ocorrencia_id}</span>`;
            }
            
            html += `<tr>
                <td>${o.data.split('-').reverse().join('/')}</td>
                <td>${o.nome_funcionario}</td>
                <td>${o.tipo.replace(/_/g, ' ')}</td>
                <td>${o.observacao || '-'}</td>
                <td>${anulacaoInfo}</td>
                <td><button class="btn btn-danger" style="padding:6px 12px;" onclick="deletarOcorrencia(${o.id})">Deletar</button></td>
            </tr>`;
        });
        
        html += '</tbody></table>';
        document.getElementById('listaOcorrencias').innerHTML = html;

    } catch (error) {
        document.getElementById('listaOcorrencias').innerHTML = 
            '<p style="color:red;">Erro ao carregar ocorrências</p>';
    }
}

async function deletarOcorrencia(id) {
    if (!confirm('Deseja realmente deletar esta ocorrência?')) return;

    try {
        const res = await fetch(`/api/ocorrencias/${id}`, {method: 'DELETE'});
        
        if (res.ok) {
            mostrarAlerta('Ocorrência deletada com sucesso!');
            carregarOcorrencias();
            carregarDashboard();
        } else {
            const erro = await res.json();
            mostrarAlerta(erro.detail, 'error');
        }
    } catch (error) {
        mostrarAlerta('Erro ao deletar ocorrência', 'error');
    }
}

// Relatórios
async function gerarRelatorio(e) {
    e.preventDefault();
    
    const dataInicio = document.getElementById('relDataInicio').value;
    const dataFim = document.getElementById('relDataFim').value;

    try {
        const res = await fetch('/api/relatorio/geral', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                data_inicio: dataInicio,
                data_fim: dataFim
            })
        });

        const relatorio = await res.json();
        
        let html = `
            <div style="background:#f8f9fa;padding:20px;border-radius:8px;margin-bottom:20px;">
                <h3>Período: ${dataInicio.split('-').reverse().join('/')} a ${dataFim.split('-').reverse().join('/')}</h3>
                <p><strong>Total de Funcionários:</strong> ${relatorio.total_funcionarios}</p>
                <p><strong>Receberão Bônus:</strong> <span class="badge badge-success">${relatorio.recebem_bonus}</span></p>
                <p><strong>Não Receberão:</strong> <span class="badge badge-danger">${relatorio.nao_recebem_bonus}</span></p>
            </div>
        `;

        html += '<table><thead><tr><th>ID</th><th>Nome</th><th>Ocorrências</th><th>Atestados</th><th>Bônus</th><th>Status</th></tr></thead><tbody>';
        
        relatorio.funcionarios.forEach(f => {
            const status = f.recebe_bonus 
                ? '<span class="badge badge-success">✓ Recebe</span>'
                : '<span class="badge badge-danger">✗ Não Recebe</span>';
            
            html += `<tr>
                <td>${f.funcionario_id}</td>
                <td>${f.nome}</td>
                <td>${f.total_ocorrencias}</td>
                <td>${f.atestados}/2</td>
                <td><strong>${f.bonus_percentual}%</strong></td>
                <td>${status}</td>
            </tr>`;
        });
        
        html += '</tbody></table>';
        document.getElementById('resultadoRelatorio').innerHTML = html;

    } catch (error) {
        mostrarAlerta('Erro ao gerar relatório', 'error');
    }
}

// Regras
async function carregarRegras() {
    try {
        const res = await fetch('/api/regras');
        const regras = await res.json();
        
        let html = '<table><thead><tr><th>Tipo</th><th>Categoria</th><th>Impacto</th><th>Descrição</th></tr></thead><tbody>';
        
        regras.forEach(r => {
            let impacto = '';
            if (r.categoria === 'elimina') {
                impacto = '<span class="badge badge-danger">Elimina Bônus</span>';
            } else if (r.categoria === 'limite') {
                impacto = `<span class="badge badge-danger">Limite: ${r.limite}</span>`;
            } else {
                impacto = `<span class="badge" style="background:#fff3bf;color:#c92a2a;">-${r.desconto}%</span>`;
            }
            
            html += `<tr>
                <td><strong>${r.tipo.replace(/_/g, ' ')}</strong></td>
                <td>${r.categoria}</td>
                <td>${impacto}</td>
                <td>${r.descricao}</td>
            </tr>`;
        });
        
        html += '</tbody></table>';
        document.getElementById('listaRegras').innerHTML = html;

    } catch (error) {
        document.getElementById('listaRegras').innerHTML = 
            '<p style="color:red;">Erro ao carregar regras</p>';
    }
}

// Carrega tipos de ocorrência
async function carregarTiposOcorrencia() {
    try {
        const res = await fetch('/api/regras');
        const regras = await res.json();
        
        const select = document.getElementById('ocorrenciaTipo');
        select.innerHTML = '<option value="">Selecione...</option>';
        
        regras.forEach(r => {
            select.innerHTML += `<option value="${r.tipo}">${r.tipo.replace(/_/g, ' ')} - ${r.descricao}</option>`;
        });
    } catch (error) {
        console.error('Erro ao carregar tipos:', error);
    }
}

// Inicialização
window.onload = function() {
    carregarDashboard();
    carregarFuncionarios();
    carregarTiposOcorrencia();
    
    // Adiciona event listener para carregar ocorrências pendentes
    const selectFuncionario = document.getElementById('funcionario_id');
    if (selectFuncionario) {
        selectFuncionario.addEventListener('change', function() {
            carregarOcorrenciasPendentes(this.value);
        });
    }
};
