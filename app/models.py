from pydantic import BaseModel
from typing import Optional
from enum import Enum

# Enum para as funções disponíveis
class FuncaoEnumFuncionario(str, Enum):
    LIDER = "LIDER"
    OPERADOR = "OPERADOR" 
    AJUDANTE = "AJUDANTE"

class Funcionario(BaseModel):
    nome: str
    funcao: FuncaoEnumFuncionario

class FuncionarioUpdate(BaseModel):
    nome: Optional[str] = None
    funcao: Optional[FuncaoEnumFuncionario] = None
    ativo: Optional[bool] = None

class Ocorrencia(BaseModel):
    funcionario_id: int
    tipo: str
    data: str
    observacao: Optional[str] = None
    anula_ocorrencia_id: Optional[int] = None

class PeriodoRelatorio(BaseModel):
    data_inicio: str
    data_fim: str

class OcorrenciaComAnulacao(BaseModel):
    id: int
    funcionario_id: int
    nome_funcionario: str
    tipo: str
    data: str
    observacao: Optional[str]
    anula_ocorrencia_id: Optional[int]
    registrado_em: str
    ocorrencia_anulada: Optional[dict] = None

# Modelos para regras
class RegraBonus(BaseModel):
    tipo: str
    categoria: str
    desconto: float
    limite: Optional[int] = None
    descricao: Optional[str] = None

class RegraBonusUpdate(BaseModel):
    categoria: Optional[str] = None
    desconto: Optional[float] = None
    limite: Optional[int] = None
    descricao: Optional[str] = None