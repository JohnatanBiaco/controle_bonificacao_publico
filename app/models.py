from pydantic import BaseModel
from typing import Optional

class Funcionario(BaseModel):
    id: str  # Matrícula como ID
    nome: str
    funcao: Optional[str] = None

class FuncionarioUpdate(BaseModel):
    nome: Optional[str] = None
    funcao: Optional[str] = None
    ativo: Optional[bool] = None

class Ocorrencia(BaseModel):
    funcionario_id: str  # Matrícula do funcionário
    tipo: str
    data: str
    observacao: Optional[str] = None
    anula_ocorrencia_id: Optional[int] = None  # Nova campo: ID da ocorrência que este atestado anula

class PeriodoRelatorio(BaseModel):
    data_inicio: str
    data_fim: str

class OcorrenciaComAnulacao(BaseModel):
    id: int
    funcionario_id: str
    nome_funcionario: str
    tipo: str
    data: str
    observacao: Optional[str]
    anula_ocorrencia_id: Optional[int]
    registrado_em: str
    ocorrencia_anulada: Optional[dict] = None  # Detalhes da ocorrência anulada
