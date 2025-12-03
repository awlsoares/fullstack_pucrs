from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo
from sqlalchemy import event, CheckConstraint, Integer, Column, Date, Numeric
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.types import JSON

db = SQLAlchemy()

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cnpj = db.Column(db.String(18), nullable=False)
    observacao = db.Column(db.String(300), nullable=True)

    def __repr__(self):
        return f"ID {self.id} Cliente {self.nome} CNPJ {self.cnpj}."

class Proposta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_cadastro = db.Column(db.Date, default=date.today, nullable=False)

    numero_proposta= db.Column(db.String(10), nullable=False)
    versao = db.Column(db.Integer, default=0, nullable=False)
    # Se alterar algum valor da proposta, será criada uma nova versão
    # com os novos valores e a versão "0" não poderá ser alterada pelo usuário.

    data_envio = db.Column(db.Date, default=date.today, nullable=False)

    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    cliente = db.relationship('Cliente', backref=db.backref('propostas', lazy=True))

    escopo = db.Column(db.String(300), nullable=False)

    contratos_multiplos =  db.Column(db.Boolean, default=False, nullable=True) # "True" ou "False"
    # "True": A Proposta terá vários lançamentos mensais (contratos), por exemplo uma proposta de
    # consultoria mensal. Neste caso será cadastrado no sistema uma Proposta e será criado no 
    # sistema um Contrato para cada mês, referindo-se sempre ao mesmo número de Proposta.
    
    valor_assinatura = db.Column(db.Float, default=0.0, nullable=False)
    valor_protocolo = db.Column(db.Float, default=0.0, nullable=False)
    valor_conclusao = db.Column(db.Float, default=0.0, nullable=False)
    
    status_proposta = db.Column(db.String(25), default="Aguardando Aprovação", nullable=False) # Aprovado / Reprovado / Cancelado

    observacao = db.Column(db.String(300), nullable=True)

    # contrato_id = db.Column(db.Integer, db.ForeignKey('contrato.id'), nullable=True)
    # contrato = db.relationship('Contrato', backref=db.backref('propostas', lazy=True))

    historico = db.Column(MutableList.as_mutable(JSON), default=list)  # Guarda versões anteriores

    contratos = db.relationship('Contrato', back_populates='proposta', lazy=True)

    def criar_nova_versao(self, nova_assinatura, novo_protocolo, novo_conclusao, nova_data_envio):
        print("Entrou em models - criar nova versão!")

        # Adiciona versão atual ao histórico
        self.historico.append({
            "versao": self.versao,
            "data_envio": self.data_envio.isoformat(),
            "cliente_id": self.cliente_id,
            "cliente_nome": self.cliente.nome,
            "valor_assinatura": self.valor_assinatura,
            "valor_protocolo": self.valor_protocolo,
            "valor_conclusao": self.valor_conclusao
        })

        # Atualiza para nova versão
        self.versao += 1
        self.valor_assinatura = nova_assinatura
        self.valor_protocolo = novo_protocolo
        self.valor_conclusao = novo_conclusao
        self.data_envio = nova_data_envio

        print(self.historico)


    def __repr__(self):
        return f"Nº {self.numero_proposta} | Versão {self.versao} | Cliente: {self.cliente.nome} | Total R$ {self.valor_assinatura + self.valor_protocolo + self.valor_conclusao}"
   
class Contrato(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_cadastro = db.Column(db.Date, default=date.today, nullable=False)
    
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    cliente = db.relationship('Cliente', backref=db.backref('contratos', lazy=True))
    
    escopo = db.Column(db.String(300), nullable=False)
    data_assinatura = db.Column(db.Date, default=date.today, nullable=False)
    
    valor_assinatura = db.Column(db.Float, nullable=False)
    status_assinatura = db.Column(db.Boolean, default=False) # False = Não Faturado / True = Faturado
    data_faturamento_assinatura = db.Column(db.Date, default=date.today, nullable=False)
    
    valor_protocolo = db.Column(db.Float, nullable=False)
    status_protocolo = db.Column(db.Boolean, default=False)
    data_faturamento_protocolo = db.Column(db.Date, default=date.today, nullable=False)
    
    valor_conclusao = db.Column(db.Float, nullable=True)
    status_conclusao = db.Column(db.Boolean, default=False, nullable=True)
    data_faturamento_conclusao = db.Column(db.Date, default=date.today, nullable=True)
        
    status_contrato = db.Column(db.String(25), default="Parado", nullable=False) # "Em Andamento"/ "Finalizado" / "Cancelado"

    numero_contrato= db.Column(db.String(10), nullable=False)

    observacao = db.Column(db.String(300), nullable=True)

    proposta_id = db.Column(db.Integer, db.ForeignKey('proposta.id'), nullable=True)
    proposta = db.relationship('Proposta', back_populates='contratos')

    def __repr__(self):
        return f"<Contrato {self.escopo} - Cliente: {self.cliente.nome}>"

class Banco(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_cadastro = db.Column(db.Date, default=date.today, nullable=False)

    nome = db.Column(db.String(30), nullable=False)
    numero_conta = db.Column(db.String(20), nullable=False)
    saldo = db.Column(db.Float, default=0.00, nullable=False)
    observacao = db.Column(db.String(300), nullable=False)

    def __repr__(self):
        return f"<Banco {self.numero_conta} - Conta: {self.numero_conta}>"
    
class NotaFiscal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_cadastro = db.Column(db.Date, default=date.today, nullable=False)

    numero_nf= db.Column(db.Integer, nullable=False)
    data_emissao = db.Column(db.Date, default=date.today, nullable=False)
    
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    cliente = db.relationship('Cliente', backref=db.backref('notas_fiscais', lazy=True))
    
    valor_bruto = db.Column(db.Float, nullable=False)
    valor_liquido = db.Column(db.Float, nullable=False)

    forma_de_pagamento = db.Column(db.String(10), nullable=False) # "Boleto", "Pix", "TED", "Outros"

    boleto = db.Column(db.String(15), nullable=True)

    banco_id = db.Column(db.Integer, db.ForeignKey('banco.id'), nullable=False)
    banco = db.relationship('Banco', backref=db.backref('notas_fiscais', lazy=True))

    data_vencimento = db.Column(db.Date, default=date.today, nullable=False)
    data_pagamento = db.Column(db.Date, nullable=True)

    status_pagamento = db.Column(db.String(15), nullable=False) # 'Recebido', 'No Prazo' ou 'Cancelado'

    contrato_id = db.Column(db.Integer, db.ForeignKey('contrato.id'), nullable=False)
    contrato = db.relationship('Contrato', backref=db.backref('notas_fiscais', lazy=True))

    tipo_servico = db.Column(db.String(12), nullable=False) # 'Assinatura', 'Protocolo' ou 'Conclusão'

    observacao = db.Column(db.String(300), nullable=True)
    
    def __repr__(self):
        return f"<Nota Fiscal {self.numero_nf} - Cliente: {self.cliente} - Valor Liquido: {self.valor_liquido}>"

class SaldoCaixaMensal(db.Model):
    __tablename__ = 'saldo_caixa_mensal'

    id = Column(Integer, primary_key=True)
    ano = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    saldo_final = Column(Numeric(12, 2), nullable=False)
    criado_em = db.Column(db.Date, default=date.today, nullable=False)
    
class Movimentacao(db.Model):
    __tablename__ = 'movimentacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    
    data_cadastro = db.Column(db.Date, default=date.today, nullable=False)
    operacao = db.Column(db.String(10), nullable=False)  # "Entrada", "Saida"
    
    data = db.Column(db.Date, default=date.today, nullable=False)
    descricao = db.Column(db.String(300), nullable=True)
    forma_de_pagamento = db.Column(db.String(20), nullable=False)  # "Boleto", "Pix", "TED", "Outros"
    status_pagamento = db.Column(db.String(15), nullable=False)  # 'Recebido', 'No Prazo' ou 'Cancelado'
    mes = db.Column(db.Integer, nullable=False)  # 1-12
    ano = db.Column(db.Integer, nullable=False)  # 2024, 2025, etc.
    
    movimentacao_tipo = db.Column(db.String(30), nullable=False)  # "Despesa", "Investimento", "Lucro", "Receita", "Despesas Administrativas"
    movimentacao_categoria = db.Column(db.String(30), nullable=False)  # "Alimentacao", "Aluguel", "Rendimento"
    
    valor = db.Column(db.Float, nullable=False)
    observacao = db.Column(db.String(300), nullable=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.data and (not self.mes or not self.ano):
            self.mes = self.data.month
            self.ano = self.data.year
    
    def __repr__(self):
        return f"<Movimentacao: {self.operacao} - Data: {self.data} - Descricao: {self.descricao} - Valor: {self.valor}>"

@event.listens_for(Movimentacao.data, 'set')
def update_mes_ano(target, value, oldvalue, initiator):
    if value:
        target.mes = value.month
        target.ano = value.year