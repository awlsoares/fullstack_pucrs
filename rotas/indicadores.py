from sqlalchemy import extract, func
from flask import Blueprint, render_template
from models import db, Proposta, Contrato, NotaFiscal
from datetime import date

# Criação do Blueprint para o módulo de indicadores
indicadores_bp = Blueprint('indicadores', __name__)

def qtd_propostas_status():
    """
    Calcula os indicadores de propostas com base em seus status.
    """
    # Obtendo o total de propostas
    propostas_total = Proposta.query.count()  # Conta o total de propostas na base de dados
    print(f"------------ Total de Propostas: {propostas_total}.")

    # Obtendo as propostas por status
    propostas_aprovadas = Proposta.query.filter(Proposta.status_proposta == 'Aprovado').count()
    propostas_reprovadas = Proposta.query.filter(Proposta.status_proposta == 'Reprovado').count()

    # Calculando o número de propostas canceladas
    propostas_canceladas = propostas_total - propostas_aprovadas - propostas_reprovadas

    # Retornando os resultados como um dicionário
    return {
        'propostas_total': propostas_total,
        'propostas_aprovadas': propostas_aprovadas,
        'propostas_reprovadas': propostas_reprovadas,
        'propostas_canceladas': propostas_canceladas
    }

def qtd_contratos_status():
    """
    Calcula os indicadores de contratos com base em seus status.
    """
    # Obtendo o total de contratos
    contratos_total = Contrato.query.count()  # Conta o total de contratos na base de dados
    print(f"------------ Total de Contratos: {contratos_total}.")

    # Obtendo as contratos por status
    contratos_parados = Contrato.query.filter(Contrato.status_contrato == 'Parado').count()
    contratos_em_andamento = Contrato.query.filter(Contrato.status_contrato == 'Em Andamento').count()
    contratos_concluidos = Contrato.query.filter(Contrato.status_contrato == 'Finalizado').count()

    # Calculando o número de contratos cancelados
    contratos_cancelados = contratos_total - contratos_parados - contratos_em_andamento - contratos_concluidos

    # Retornando os resultados como um dicionário
    return {
        'contratos_total': contratos_total,
        'contratos_parados': contratos_parados,
        'contratos_em_andamento': contratos_em_andamento,
        'contratos_concluidos': contratos_concluidos,
        'contratos_cancelados': contratos_cancelados
    }

def qtd_nfs_status():
    """
    Calcula os indicadores de nfs com base em seus status.
    """
    # Obtendo o total de nfs
    nfs_total = NotaFiscal.query.count()  # Conta o total de nfs na base de dados
    print(f"------------ Total de Notas Fiscais: {nfs_total}.")

    # Notas fiscais Recebidas
    nfs_recebidas = NotaFiscal.query.filter(NotaFiscal.status_pagamento == 'Recebido').count()

    # Notas fiscais atrasadas (data_vencimento < hoje e data_pagamento ainda é None)
    nfs_atrasadas = NotaFiscal.query.filter(
        NotaFiscal.data_vencimento < date.today(),
        NotaFiscal.data_pagamento == None
    ).count()

    # Notas fiscais no prazo (data_vencimento >= hoje e data_pagamento ainda é None)
    nfs_no_prazo = NotaFiscal.query.filter(
        NotaFiscal.data_vencimento >= date.today(),
        NotaFiscal.data_pagamento == None
    ).count()


    # Retornando os resultados como um dicionário
    return {
        'nfs_total': nfs_total,
        'nfs_recebidas': nfs_recebidas,
        'nfs_atrasadas': nfs_atrasadas,
        'nfs_no_prazo': nfs_no_prazo
    }

def valor_nfs_status():
    print("--------------- Entrou em valor_nfs_status().")
    """
    Calcula os indicadores de nfs com base em seus status.
    """
    # Soma da coluna valor_bruto de todas as notas fiscais
    soma_valor_bruto_total = NotaFiscal.query.with_entities(func.sum(NotaFiscal.valor_bruto)).scalar()
    if soma_valor_bruto_total == None:
        soma_valor_bruto_total = 0

    # Soma da coluna valor_bruto filtrada pelo status 'Recebido'
    soma_valor_bruto_recebido = NotaFiscal.query.with_entities(func.sum(NotaFiscal.valor_bruto)).filter(NotaFiscal.status_pagamento == 'Recebido').scalar()
    if soma_valor_bruto_recebido == None:
        soma_valor_bruto_recebido = 0

    print(f"Soma do valor bruto de todas as notas fiscais: {soma_valor_bruto_total}")
    print(f"Soma do valor bruto das notas fiscais recebidas: {soma_valor_bruto_recebido}")

   # Soma dos valores brutos das notas fiscais atrasadas
    soma_valor_bruto_atrasadas = NotaFiscal.query.with_entities(func.sum(NotaFiscal.valor_bruto)).filter(
        NotaFiscal.data_vencimento < date.today(),  # Condição de atraso
        NotaFiscal.data_pagamento == None          # Ainda não foi paga
    ).scalar()
    if soma_valor_bruto_atrasadas == None:
        soma_valor_bruto_atrasadas = 0

    # Soma dos valores brutos das notas fiscais no prazo
    soma_valor_bruto_no_prazo = NotaFiscal.query.with_entities(func.sum(NotaFiscal.valor_bruto)).filter(
        NotaFiscal.data_vencimento >= date.today(), # Ainda dentro do prazo
        NotaFiscal.data_pagamento == None           # Ainda não foi paga
    ).scalar()
    if soma_valor_bruto_no_prazo == None:
        soma_valor_bruto_no_prazo = 0

    print(f"Soma do valor bruto das notas fiscais atrasadas: {soma_valor_bruto_atrasadas}")
    print(f"Soma do valor bruto das notas fiscais no prazo: {soma_valor_bruto_no_prazo}")


    # Retornando os resultados como um dicionário
    return {
        'soma_valor_bruto_total': soma_valor_bruto_total,
        'soma_valor_bruto_recebido': soma_valor_bruto_recebido,
        'soma_valor_bruto_atrasadas': soma_valor_bruto_atrasadas,
        'soma_valor_bruto_no_prazo': soma_valor_bruto_no_prazo
    }

def calcular_faturamento_anual():
    """
    Gera dois dicionários:
    1. Soma do valor bruto por ano.
    2. Soma do valor bruto por ano e mês (dicionário aninhado).
    """

    # Consulta todas as notas fiscais
    notas_fiscais = NotaFiscal.query.all()

    # Dicionário para armazenar soma do valor bruto por ano
    faturamento_por_ano = {}

    # Dicionário aninhado para armazenar soma do valor bruto por ano e mês
    faturamento_por_ano_mes = {}

    # Itera sobre todas as notas fiscais para processar os dados
    for nota in notas_fiscais:
        ano = nota.data_emissao.year  # Obtém o ano da data de emissão
        mes = nota.data_emissao.month  # Obtém o mês da data de emissão

        # Soma do valor bruto por ano
        if ano not in faturamento_por_ano:
            faturamento_por_ano[ano] = 0
        faturamento_por_ano[ano] += nota.valor_bruto

        # Soma do valor bruto por ano e mês
        if ano not in faturamento_por_ano_mes:
            faturamento_por_ano_mes[ano] = {}  # Cria um dicionário para o ano
        if mes not in faturamento_por_ano_mes[ano]:
            faturamento_por_ano_mes[ano][mes] = 0
        faturamento_por_ano_mes[ano][mes] += nota.valor_bruto

        print("Faturamento Ano: ", faturamento_por_ano)
        print("Faturamento Mês: ", faturamento_por_ano_mes)
    # Retorna os dois dicionários
    return faturamento_por_ano, faturamento_por_ano_mes
    

@indicadores_bp.route('/home', methods=['GET'])
def kpi():
    
    # Obtendo os indicadores de propostas
    dados_propostas = qtd_propostas_status()
    dados_contratos = qtd_contratos_status()
    dados_nfs = qtd_nfs_status()
    faturamento_anual, faturamento_anual_mensal = calcular_faturamento_anual()
    dados_recebimentos_nfs = valor_nfs_status()

    print("Faturamento por Ano:")
    print(faturamento_anual)

    print("\nFaturamento por Ano e Mês:")
    print(faturamento_anual_mensal)

    # Obtendo as nfs "Não Recebidas"
    nfs_nao_recebidas = NotaFiscal.query.filter(NotaFiscal.data_pagamento == None).count()
    print("------------ QTD NFs não recebidas: ", nfs_nao_recebidas)

    # Renderizando o template e passando os dados
    return render_template(
        'index_kpi.html',
        
        propostas_total = dados_propostas['propostas_total'],
        propostas_aprovadas = dados_propostas['propostas_aprovadas'],
        propostas_reprovadas = dados_propostas['propostas_reprovadas'],
        propostas_canceladas = dados_propostas['propostas_canceladas'],

       
        contratos_total = dados_contratos['contratos_total'],
        contratos_parados = dados_contratos['contratos_parados'],
        contratos_em_andamento = dados_contratos['contratos_em_andamento'],
        contratos_concluidos = dados_contratos['contratos_concluidos'],
        contratos_cancelados = dados_contratos['contratos_cancelados'],

        nfs_total = dados_nfs['nfs_total'],
        nfs_recebidas = dados_nfs['nfs_recebidas'],
        nfs_atrasadas = dados_nfs['nfs_atrasadas'],
        nfs_no_prazo = dados_nfs['nfs_no_prazo'],

        soma_valor_bruto_total = dados_recebimentos_nfs['soma_valor_bruto_total'],
        soma_valor_bruto_recebido = dados_recebimentos_nfs['soma_valor_bruto_recebido'],
        soma_valor_bruto_atrasadas = dados_recebimentos_nfs['soma_valor_bruto_atrasadas'],
        soma_valor_bruto_no_prazo = dados_recebimentos_nfs['soma_valor_bruto_no_prazo'],

        faturamento_anual = faturamento_anual,
        faturamento_anual_mensal = faturamento_anual_mensal
        )
