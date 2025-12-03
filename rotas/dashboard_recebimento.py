from sqlalchemy import extract
from flask import Blueprint, render_template, request
from models import db, Contrato, NotaFiscal
from datetime import date

dashboard_recebimento_bp = Blueprint('dashboard_recebimento', __name__)

@dashboard_recebimento_bp.route('/')
def dashboard_index():
    
    return render_template('index.html')

def grafico_1(ano):
    
    # Inicialização dos vetores para os 12 meses do ano
    assinatura = [0] * 12
    protocolo = [0] * 12
    conclusao = [0] * 12
    recebido = [0] * 12

    # Consulta ao banco de dados filtrando nfs assinaturas recebidas
    nfs_assinatura_paga = NotaFiscal.query.filter(
        NotaFiscal.tipo_servico == 'Assinatura',
        NotaFiscal.status_pagamento == 'Recebido', 
        NotaFiscal.data_pagamento != None,
        extract('year', NotaFiscal.data_pagamento) == ano
    ).all()

    for nf in nfs_assinatura_paga:
        if nf.data_pagamento.year == ano:
            posicao = nf.data_pagamento.month - 1
            assinatura[posicao] += nf.valor_liquido
    
    # Consulta ao banco de dados filtrando nfs protocolos recebidos
    nfs_protocolo_paga = NotaFiscal.query.filter(
        NotaFiscal.tipo_servico == 'Protocolo',
        NotaFiscal.status_pagamento == 'Recebido', 
        NotaFiscal.data_pagamento != None,
        extract('year', NotaFiscal.data_pagamento) == ano
    ).all()

    for nf in nfs_protocolo_paga:
        if nf.data_pagamento.year == ano:
            posicao = nf.data_pagamento.month - 1
            protocolo[posicao] += nf.valor_liquido

    # Consulta ao banco de dados filtrando aprovações recebidas
    nfs_conclusao_paga = NotaFiscal.query.filter(
        NotaFiscal.tipo_servico == 'Conclusão',
        NotaFiscal.status_pagamento == 'Recebido', 
        NotaFiscal.data_pagamento != None,
        extract('year', NotaFiscal.data_pagamento) == ano
    ).all()

    for nf in nfs_conclusao_paga:
        if nf.data_pagamento.year == ano:
            posicao = nf.data_pagamento.month - 1
            conclusao[posicao] += nf.valor_liquido

    # Soma os 3 vetores (assinatura, protocolo, conclusao)
    for indice in range(12):
        recebido[indice] = assinatura[indice] + protocolo[indice] + conclusao[indice]

    # Executa a consulta para obter os anos disponíveis
    anos_existentes = db.session.query(
            extract('year', NotaFiscal.data_pagamento).label('ano')
        ).filter(NotaFiscal.data_pagamento != None).all()

    # Extrai os anos como inteiros
    anos_existentes = [int(ano.ano) for ano in anos_existentes]
    
    # Combina todas as listas e remove duplicatas usando `set`
    anos_disponiveis = list(set(anos_existentes))

    # Ordena os anos de forma crescente
    anos_disponiveis.sort()

    valores = [
        ["{:.2f}".format(valor) for valor in assinatura],  # Formata cada valor em assinatura
        ["{:.2f}".format(valor) for valor in protocolo],  # Formata cada valor em protocolo
        ["{:.2f}".format(valor) for valor in conclusao],  # Formata cada valor em conclusao
        ["{:.2f}".format(valor) for valor in recebido],   # Formata cada valor em recebido
        ano,
        anos_disponiveis
    ]

    return valores

@dashboard_recebimento_bp.route('/grafico_recebimento', methods=['GET'])
def dashboard_grafico_recebimento():
    # Obtém o ano atual ou o ano selecionado pelo usuário
    hoje = date.today()
    ano = request.args.get('ano', hoje.year, type=int)

    grafico = grafico_1(ano)

    recebimentos = []

    # Consulta ao banco de dados filtrando nfs assinaturas recebidas
    nfs_assinatura_paga = NotaFiscal.query.filter(
        NotaFiscal.tipo_servico == 'Assinatura',
        NotaFiscal.status_pagamento == 'Recebido',
        NotaFiscal.data_pagamento != None,
        extract('year', NotaFiscal.data_pagamento) == ano,
    ).all() 

    for nf in nfs_assinatura_paga:
        recebimentos.append({"numero_nf": nf.numero_nf,
                             "cliente": nf.cliente.nome, 
                             "contrato": nf.contrato, 
                             "banco": nf.banco,
                             "data_pagamento": nf.data_pagamento,
                             "valor_bruto": round(nf.valor_bruto, 2),  # Formata valor_bruto
                             "valor_liquido": round(nf.valor_liquido, 2), # Formata valor_liquido
                             "tipo": "Assinatura"
                             })

    # Consulta ao banco de dados filtrando nfs protocolos recebidos
    nfs_protocolo_pago = NotaFiscal.query.filter(
        NotaFiscal.tipo_servico == 'Protocolo',
        NotaFiscal.status_pagamento == 'Recebido',
        NotaFiscal.data_pagamento != None,
        extract('year', NotaFiscal.data_pagamento) == ano,
    ).all() 

    for nf in nfs_protocolo_pago: 
        recebimentos.append({"numero_nf": nf.numero_nf,
                             "cliente": nf.cliente.nome, 
                             "contrato": nf.contrato, 
                             "banco": nf.banco,
                             "data_pagamento": nf.data_pagamento,
                             "valor_bruto": round(nf.valor_bruto, 2),  # Formata valor_bruto
                             "valor_liquido": round(nf.valor_liquido, 2), # Formata valor_liquido
                             "tipo": "Protocolo"
                             })
    
    # Consulta ao banco de dados filtrando nfs conclusao recebidos
    nfs_conclusao_paga = NotaFiscal.query.filter(
        NotaFiscal.tipo_servico == 'Conclusão',
        NotaFiscal.status_pagamento == 'Recebido',
        NotaFiscal.data_pagamento != None,
        extract('year', NotaFiscal.data_pagamento) == ano,
    ).all() 

    for nf in nfs_conclusao_paga: 
        recebimentos.append({"numero_nf": nf.numero_nf,
                             "cliente": nf.cliente.nome, 
                             "contrato": nf.contrato, 
                             "banco": nf.banco,
                             "data_pagamento": nf.data_pagamento,
                             "valor_bruto": round(nf.valor_bruto, 2),  # Formata valor_bruto
                             "valor_liquido": round(nf.valor_liquido, 2), # Formata valor_liquido
                             "tipo": "Conclusão"
                             })


    return render_template('dashboard/grafico_barras_recebimento.html',
        assinatura=grafico[0],
        protocolo=grafico[1],
        conclusao=grafico[2],
        recebido=grafico[3],
        ano=grafico[4],
        anos_disponiveis=grafico[5], 
        recebimentos=recebimentos
        )

@dashboard_recebimento_bp.route('/recebimentos/<int:ano>/<int:mes>', methods=['GET', 'POST'])
def listar_recebimentos_mes(ano, mes):

    grafico = grafico_1(ano)

    recebimentos = []

    # -------------------------------------------------------------------
    # Lista de condições para a consulta
    filtros = [
        NotaFiscal.tipo_servico == 'Assinatura',
        NotaFiscal.status_pagamento == 'Recebido',
        NotaFiscal.data_pagamento != None,
        extract('year', NotaFiscal.data_pagamento) == ano,
    ]

    # Adiciona o filtro do mês apenas se `mes` for diferente de 0
    if mes != 0:
        filtros.append(extract('month', NotaFiscal.data_pagamento) == mes)

    # Consulta ao banco de dados filtrando assinaturas recebidas
    nfs_assinatura_paga = NotaFiscal.query.filter(*filtros).all()

    for nf in nfs_assinatura_paga: 
        recebimentos.append({"numero_nf": nf.numero_nf,
                             "cliente": nf.cliente.nome, 
                             "contrato": nf.contrato, 
                             "banco": nf.banco,
                             "data_pagamento": nf.data_pagamento,
                             "valor_bruto": round(nf.valor_bruto, 2),  # Formata valor_bruto
                             "valor_liquido": round(nf.valor_liquido, 2), # Formata valor_liquido
                             "tipo": "Assinatura"
                             })

    # -------------------------------------------------------------------
    # Lista de condições para a consulta
    filtros = [
        NotaFiscal.tipo_servico == 'Protocolo',
        NotaFiscal.status_pagamento == 'Recebido',
        NotaFiscal.data_pagamento != None,
        extract('year', NotaFiscal.data_pagamento) == ano,
    ]

    # Adiciona o filtro do mês apenas se `mes` for diferente de 0
    if mes != 0:
        filtros.append(extract('month', NotaFiscal.data_pagamento) == mes)

    # Consulta ao banco de dados filtrando nfs prootocolo recebidas
    nfs_protocolo_paga = NotaFiscal.query.filter(*filtros).all()

    for nf in nfs_protocolo_paga: 
        recebimentos.append({"numero_nf": nf.numero_nf,
                             "cliente": nf.cliente.nome, 
                             "contrato": nf.contrato, 
                             "banco": nf.banco,
                             "data_pagamento": nf.data_pagamento,
                             "valor_bruto": round(nf.valor_bruto, 2),  # Formata valor_bruto
                             "valor_liquido": round(nf.valor_liquido, 2), # Formata valor_liquido
                             "tipo": "Protocolo"
                             })
    
    # -------------------------------------------------------------------
    # Lista de condições para a consulta
    filtros = [
        NotaFiscal.tipo_servico == 'Conclusão',
        NotaFiscal.status_pagamento == 'Recebido',
        NotaFiscal.data_pagamento != None,
        extract('year', NotaFiscal.data_pagamento) == ano,
    ]

    # Adiciona o filtro do mês apenas se `mes` for diferente de 0
    if mes != 0:
        filtros.append(extract('month', NotaFiscal.data_pagamento) == mes)

    # Consulta ao banco de dados filtrando nfs prootocolo recebidas
    nfs_conclusao_paga = NotaFiscal.query.filter(*filtros).all()

    for nf in nfs_conclusao_paga: 
        recebimentos.append({"numero_nf": nf.numero_nf,
                             "cliente": nf.cliente.nome, 
                             "contrato": nf.contrato, 
                             "banco": nf.banco,
                             "data_pagamento": nf.data_pagamento,
                             "valor_bruto": round(nf.valor_bruto, 2),  # Formata valor_bruto
                             "valor_liquido": round(nf.valor_liquido, 2), # Formata valor_liquido
                             "tipo": "Conclusão"
                             })
    
        
    return render_template('dashboard/grafico_barras_recebimento.html',
        assinatura=grafico[0],
        protocolo=grafico[1],
        conclusao=grafico[2],
        recebido=grafico[3],
        ano=grafico[4],
        anos_disponiveis=grafico[5], 
        recebimentos=recebimentos)

# -------------------------------
# Função auxiliar: gera dados do gráfico diário
# -------------------------------
def grafico_2(ano: int, mes: int):
    # Função interna para calcular quantidade de dias do mês
    def dias_do_mes(mes: int, ano: int):
        dias_por_mes = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
                        7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
        if mes == 2 and ((ano % 4 == 0 and ano % 100 != 0) or (ano % 400 == 0)):
            return 29
        return dias_por_mes[mes]

    dias = dias_do_mes(mes, ano)

    # Inicializa listas zeradas
    assinatura = [0.0] * dias
    protocolo  = [0.0] * dias
    conclusao  = [0.0] * dias
    recebido   = [0.0] * dias

    # -------------------------------
    # Consulta assinaturas
    nfs_assinatura_recebida = NotaFiscal.query.filter(
        NotaFiscal.tipo_servico == 'Assinatura',
        NotaFiscal.status_pagamento == 'Recebido', 
        NotaFiscal.data_pagamento != None,
        extract('year', NotaFiscal.data_pagamento) == ano,
        extract('month', NotaFiscal.data_pagamento) == mes
    ).all()

    for nf in nfs_assinatura_recebida:
        dia = nf.data_pagamento.day - 1
        assinatura[dia] += float(nf.valor_liquido or 0)

    # -------------------------------
    # Consulta protocolos
    nfs_protocolo_recebido = NotaFiscal.query.filter(
        NotaFiscal.tipo_servico == 'Protocolo',
        NotaFiscal.status_pagamento == 'Recebido', 
        NotaFiscal.data_pagamento != None,
        extract('year', NotaFiscal.data_pagamento) == ano,
        extract('month', NotaFiscal.data_pagamento) == mes
    ).all()

    for nf in nfs_protocolo_recebido:
        dia = nf.data_pagamento.day - 1
        protocolo[dia] += float(nf.valor_liquido or 0)

    # -------------------------------
    # Consulta aprovações
    nfs_conclusao_recebido = NotaFiscal.query.filter(
        NotaFiscal.tipo_servico == 'Conclusão',
        NotaFiscal.status_pagamento == 'Recebido', 
        NotaFiscal.data_pagamento != None,
        extract('year', NotaFiscal.data_pagamento) == ano,
        extract('month', NotaFiscal.data_pagamento) == mes
    ).all()

    for nf in nfs_conclusao_recebido:
        dia = nf.data_pagamento.day - 1
        conclusao[dia] += float(nf.valor_liquido or 0)

    # -------------------------------
    # Total diário
    for i in range(dias):
        recebido[i] = assinatura[i] + protocolo[i] + conclusao[i]

    # Labels
    labels = [str(i+1) for i in range(dias)]

    return {
        "assinatura": [f"{v:.2f}" for v in assinatura],
        "protocolo":  [f"{v:.2f}" for v in protocolo],
        "conclusao":  [f"{v:.2f}" for v in conclusao],
        "recebido":   [f"{v:.2f}" for v in recebido],
        "labels": labels,
        "dias": dias,
        "titulo": f"Recebimento Diário - {ano}/{mes:02d}"
    }

# -------------------------------
# Route: listar faturamentos diários do mês
# -------------------------------
@dashboard_recebimento_bp.route('/recebimentos/<int:ano>/<int:mes>/diario', methods=['GET'])
def listar_recebimentos_mes_diario(ano, mes):
    grafico = grafico_2(ano, mes)
    recebimentos = []

    # -------------------------------
    # Consulta assinaturas
    nfs_assinatura_recebida = NotaFiscal.query.filter(
        NotaFiscal.tipo_servico == 'Assinatura',
        NotaFiscal.status_pagamento == 'Recebido', 
        NotaFiscal.data_pagamento != None,
        extract('year', NotaFiscal.data_pagamento) == ano,
        extract('month', NotaFiscal.data_pagamento) == mes
    ).all()

    for nf in nfs_assinatura_recebida:
        recebimentos.append({"numero_nf": nf.numero_nf,
                             "cliente": nf.cliente.nome, 
                             "contrato": nf.contrato, 
                             "banco": nf.banco,
                             "data_pagamento": nf.data_pagamento,
                             "valor_bruto": round(nf.valor_bruto, 2),  # Formata valor_bruto
                             "valor_liquido": round(nf.valor_liquido, 2), # Formata valor_liquido
                             "tipo": "Assinatura"
                             })

    # -------------------------------
    # Protocolos
    nfs_protocolo_pago = NotaFiscal.query.filter(
        NotaFiscal.tipo_servico == 'Protocolo',
        NotaFiscal.status_pagamento == 'Recebido',
        NotaFiscal.data_pagamento != None,
        extract('month', NotaFiscal.data_pagamento) == mes
    ).all()

    for nf in nfs_protocolo_pago: 
        recebimentos.append({"numero_nf": nf.numero_nf,
                             "cliente": nf.cliente.nome, 
                             "contrato": nf.contrato, 
                             "banco": nf.banco,
                             "data_pagamento": nf.data_pagamento,
                             "valor_bruto": round(nf.valor_bruto, 2),  # Formata valor_bruto
                             "valor_liquido": round(nf.valor_liquido, 2), # Formata valor_liquido
                             "tipo": "Protocolo"
                             })

    # -------------------------------
    # Consulta ao banco de dados filtrando nfs conclusao recebidos
    nfs_conclusao_paga = NotaFiscal.query.filter(
        NotaFiscal.tipo_servico == 'Conclusão',
        NotaFiscal.status_pagamento == 'Recebido',
        NotaFiscal.data_pagamento != None,
        extract('year', NotaFiscal.data_pagamento) == ano,
        extract('month', NotaFiscal.data_pagamento) == mes
    ).all()
    
    for nf in nfs_conclusao_paga: 
        recebimentos.append({"numero_nf": nf.numero_nf,
                             "cliente": nf.cliente.nome, 
                             "contrato": nf.contrato, 
                             "banco": nf.banco,
                             "data_pagamento": nf.data_pagamento,
                             "valor_bruto": round(nf.valor_bruto, 2),  # Formata valor_bruto
                             "valor_liquido": round(nf.valor_liquido, 2), # Formata valor_liquido
                             "tipo": "Conclusão"
                             })

    # -------------------------------
    # Lista de anos disponíveis (opcional)
    anos_disponiveis = sorted({nf.data_pagamento.year for nf in NotaFiscal.query.all() if nf.data_pagamento})

    return render_template(
        'dashboard/grafico_barras_recebimento_diario_no_mes.html',
        assinatura=grafico["assinatura"],
        protocolo=grafico["protocolo"],
        conclusao=grafico["conclusao"],
        recebido=grafico["recebido"],
        labels=grafico["labels"],
        dias=grafico["dias"],
        titulo=grafico["titulo"],
        ano=ano,
        mes=mes,
        anos_disponiveis=anos_disponiveis,
        recebimentos=recebimentos
    )