from sqlalchemy import extract
from flask import Blueprint, render_template, request
from models import db, Contrato
from datetime import date

dashboard_faturamento_bp = Blueprint('dashboard_faturamento', __name__)

@dashboard_faturamento_bp.route('/')
def dashboard_index():
    
    return render_template('index.html')

def grafico_1(ano):
    
    # Inicialização dos vetores para os 12 meses do ano
    assinatura = [0] * 12
    protocolo = [0] * 12
    conclusao = [0] * 12
    recebido = [0] * 12

    # Consulta ao banco de dados filtrando assinaturas recebidas
    contratos_assinatura_paga = Contrato.query.filter(
        Contrato.status_assinatura == True,
        Contrato.data_faturamento_assinatura != None,
        extract('year', Contrato.data_faturamento_assinatura) == ano
    ).all()

    for contrato in contratos_assinatura_paga:
        if contrato.data_faturamento_assinatura.year == ano:
            posicao = contrato.data_faturamento_assinatura.month - 1
            assinatura[posicao] += contrato.valor_assinatura
    
    # Consulta ao banco de dados filtrando protocolos recebidos
    contratos_protocolos_pagos = Contrato.query.filter(
        Contrato.status_protocolo == True,
        Contrato.data_faturamento_protocolo != None,
        extract('year', Contrato.data_faturamento_protocolo) == ano
    ).all()

    for contrato in contratos_protocolos_pagos:
        if contrato.data_faturamento_protocolo.year == ano:
            posicao = contrato.data_faturamento_protocolo.month - 1
            protocolo[posicao] += contrato.valor_protocolo

    # Consulta ao banco de dados filtrando aprovações recebidas
    contratos_aprovacoes_pagas = Contrato.query.filter(
        Contrato.status_conclusao == True,
        Contrato.data_faturamento_conclusao != None,
        extract('year', Contrato.data_faturamento_conclusao) == ano
    ).all()

    for contrato in contratos_aprovacoes_pagas:
        if contrato.data_faturamento_conclusao.year == ano:
            posicao = contrato.data_faturamento_conclusao.month - 1
            conclusao[posicao] += contrato.valor_conclusao

    # Soma os 3 vetores (assinatura, protocolo, conclusao)
    for indice in range(12):
        recebido[indice] = assinatura[indice] + protocolo[indice] + conclusao[indice]

    # Executa a consulta para obter os anos disponíveis
    anos_assinatura = db.session.query(
            extract('year', Contrato.data_faturamento_assinatura).label('ano')
        ).filter(Contrato.data_faturamento_assinatura != None).all()

    anos_protocolo = db.session.query(
            extract('year', Contrato.data_faturamento_protocolo).label('ano')
        ).filter(Contrato.data_faturamento_protocolo != None).all()

    anos_conclusao = db.session.query(
        extract('year', Contrato.data_faturamento_conclusao).label('ano')
    ).filter(Contrato.data_faturamento_conclusao != None).all()

    # Extrai os anos como inteiros
    anos_assinatura = [int(ano.ano) for ano in anos_assinatura]
    anos_protocolo = [int(ano.ano) for ano in anos_protocolo]
    anos_conclusao = [int(ano.ano) for ano in anos_conclusao]

    # Combina todas as listas e remove duplicatas usando `set`
    anos_disponiveis = list(set(anos_assinatura + anos_protocolo + anos_conclusao))

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

@dashboard_faturamento_bp.route('/grafico_faturamento', methods=['GET'])
def dashboard_grafico_faturamento():
    # Obtém o ano atual ou o ano selecionado pelo usuário
    hoje = date.today()
    ano = request.args.get('ano', hoje.year, type=int)

    grafico = grafico_1(ano)

    faturamentos = []

    # Consulta ao banco de dados filtrando assinaturas recebidas
    contratos_assinatura_paga = Contrato.query.filter(
        Contrato.status_assinatura == True,
        Contrato.data_faturamento_assinatura != None,
        extract('year', Contrato.data_faturamento_assinatura) == ano,
    ).all() 

    for contrato in contratos_assinatura_paga: 
        faturamentos.append({"cliente": contrato.cliente.nome, 
                             "contrato": contrato.numero_contrato, 
                             "escopo": contrato.escopo,
                             "data": contrato.data_faturamento_assinatura,
                             "valor": round(contrato.valor_assinatura, 2),
                             "tipo": "Assinatura"
                             })

    # Consulta ao banco de dados filtrando protocolos recebidos
    contratos_protocolo_pago = Contrato.query.filter(
        Contrato.status_protocolo == True,
        Contrato.data_faturamento_protocolo != None,
        extract('year', Contrato.data_faturamento_protocolo) == ano,
    ).all() 

    for contrato in contratos_protocolo_pago: 
        faturamentos.append({"cliente": contrato.cliente.nome, 
                             "contrato": contrato.numero_contrato, 
                             "escopo": contrato.escopo,
                             "data": contrato.data_faturamento_protocolo,
                             "valor": round(contrato.valor_protocolo, 2),
                             "tipo": "Protocolo"
                             })
    
    # Consulta ao banco de dados filtrando conclusao recebidos
    contratos_conclusao_paga = Contrato.query.filter(
        Contrato.status_conclusao == True,
        Contrato.data_faturamento_conclusao != None,
        extract('year', Contrato.data_faturamento_conclusao) == ano,
    ).all() 

    for contrato in contratos_conclusao_paga: 
        faturamentos.append({"cliente": contrato.cliente.nome, 
                             "contrato": contrato.numero_contrato, 
                             "escopo": contrato.escopo,
                             "data": contrato.data_faturamento_conclusao,
                             "valor": round(contrato.valor_conclusao, 2),
                             "tipo": "Conclusão"
                             })
    
    # Ordena por data crescente
    faturamentos = sorted(faturamentos, key=lambda f: f['data'])

    return render_template('dashboard/grafico_barras_faturamento.html',
        assinatura=grafico[0],
        protocolo=grafico[1],
        conclusao=grafico[2],
        recebido=grafico[3],
        ano=grafico[4],
        anos_disponiveis=grafico[5], 
        faturamentos=faturamentos
        )

@dashboard_faturamento_bp.route('/faturamentos/<int:ano>/<int:mes>', methods=['GET', 'POST'])
def listar_faturamentos_mes(ano, mes):

    grafico = grafico_1(ano)

    faturamentos = []

    # -------------------------------------------------------------------
    # Lista de condições para a consulta
    filtros = [
        Contrato.status_assinatura == True,
        Contrato.data_faturamento_assinatura != None,
        extract('year', Contrato.data_faturamento_assinatura) == ano,
    ]

    # Adiciona o filtro do mês apenas se `mes` for diferente de 0
    if mes != 0:
        filtros.append(extract('month', Contrato.data_faturamento_assinatura) == mes)

    # Consulta ao banco de dados filtrando assinaturas recebidas
    contratos_assinatura_paga = Contrato.query.filter(*filtros).all()

    for contrato in contratos_assinatura_paga: 
        faturamentos.append({"cliente": contrato.cliente.nome, 
                             "contrato": contrato.numero_contrato, 
                             "escopo": contrato.escopo,
                             "data": contrato.data_faturamento_assinatura,
                             "valor": round(contrato.valor_assinatura, 2),
                             "tipo": "Assinatura"
                             })

    # -------------------------------------------------------------------
    # Lista de condições para a consulta
    filtros = [
        Contrato.status_protocolo == True,
        Contrato.data_faturamento_protocolo != None,
        extract('year', Contrato.data_faturamento_protocolo) == ano,
    ]

    # Adiciona o filtro do mês apenas se `mes` for diferente de 0
    if mes != 0:
        filtros.append(extract('month', Contrato.data_faturamento_protocolo) == mes)

    # Consulta ao banco de dados filtrando protocolos recebidos
    contratos_protocolo_pago = Contrato.query.filter(*filtros).all()


    for contrato in contratos_protocolo_pago: 
        faturamentos.append({"cliente": contrato.cliente.nome, 
                             "contrato": contrato.numero_contrato, 
                             "escopo": contrato.escopo,
                             "data": contrato.data_faturamento_protocolo,
                             "valor": round(contrato.valor_protocolo, 2),
                             "tipo": "Protocolo"
                             })
    
    # -------------------------------------------------------------------
    filtros = [
        Contrato.status_conclusao == True,
        Contrato.data_faturamento_conclusao != None,
        extract('year', Contrato.data_faturamento_conclusao) == ano,
    ]

    # Adiciona o filtro do mês apenas se `mes` for diferente de 0
    if mes != 0:
        filtros.append(extract('month', Contrato.data_faturamento_conclusao) == mes)

    # Consulta ao banco de dados filtrando aprovações recebidas
    contratos_conclusao_paga = Contrato.query.filter(*filtros).all()

    for contrato in contratos_conclusao_paga: 
        faturamentos.append({"cliente": contrato.cliente.nome, 
                             "contrato": contrato.numero_contrato, 
                             "escopo": contrato.escopo,
                             "data": contrato.data_faturamento_conclusao,
                             "valor": round(contrato.valor_conclusao, 2),
                             "tipo": "Conclusão"
                             })
        
    return render_template('dashboard/grafico_barras_faturamento.html',
        assinatura=grafico[0],
        protocolo=grafico[1],
        conclusao=grafico[2],
        recebido=grafico[3],
        ano=grafico[4],
        anos_disponiveis=grafico[5], 
        faturamentos=faturamentos)


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
    contratos_assinatura = Contrato.query.filter(
        Contrato.status_assinatura == True,
        Contrato.data_faturamento_assinatura != None,
        extract('year', Contrato.data_faturamento_assinatura) == ano,
        extract('month', Contrato.data_faturamento_assinatura) == mes
    ).all()

    for c in contratos_assinatura:
        dia = c.data_faturamento_assinatura.day - 1
        assinatura[dia] += float(c.valor_assinatura or 0)

    # -------------------------------
    # Consulta protocolos
    contratos_protocolo = Contrato.query.filter(
        Contrato.status_protocolo == True,
        Contrato.data_faturamento_protocolo != None,
        extract('year', Contrato.data_faturamento_protocolo) == ano,
        extract('month', Contrato.data_faturamento_protocolo) == mes
    ).all()

    for c in contratos_protocolo:
        dia = c.data_faturamento_protocolo.day - 1
        protocolo[dia] += float(c.valor_protocolo or 0)

    # -------------------------------
    # Consulta aprovações
    contratos_conclusao = Contrato.query.filter(
        Contrato.status_conclusao == True,
        Contrato.data_faturamento_conclusao != None,
        extract('year', Contrato.data_faturamento_conclusao) == ano,
        extract('month', Contrato.data_faturamento_conclusao) == mes
    ).all()

    for c in contratos_conclusao:
        dia = c.data_faturamento_conclusao.day - 1
        conclusao[dia] += float(c.valor_conclusao or 0)

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
        "titulo": f"Faturamento Diário - {ano}/{mes:02d}"
    }

# -------------------------------
# Route: listar faturamentos diários do mês
# -------------------------------
@dashboard_faturamento_bp.route('/faturamentos/<int:ano>/<int:mes>/diario', methods=['GET'])
def listar_faturamentos_mes_diario(ano, mes):
    grafico = grafico_2(ano, mes)
    faturamentos = []

    # -------------------------------
    # Assinaturas
    contratos_assinatura = Contrato.query.filter(
        Contrato.status_assinatura == True,
        Contrato.data_faturamento_assinatura != None,
        extract('year', Contrato.data_faturamento_assinatura) == ano,
        extract('month', Contrato.data_faturamento_assinatura) == mes
    ).all()
    for c in contratos_assinatura:
        faturamentos.append({
            "cliente": c.cliente.nome,
            "contrato": c.numero_contrato,
            "escopo": c.escopo,
            "data": c.data_faturamento_assinatura,
            "valor": round(c.valor_assinatura or 0, 2),
            "tipo": "Assinatura"
        })

    # -------------------------------
    # Protocolos
    contratos_protocolo = Contrato.query.filter(
        Contrato.status_protocolo == True,
        Contrato.data_faturamento_protocolo != None,
        extract('year', Contrato.data_faturamento_protocolo) == ano,
        extract('month', Contrato.data_faturamento_protocolo) == mes
    ).all()
    for c in contratos_protocolo:
        faturamentos.append({
            "cliente": c.cliente.nome,
            "contrato": c.numero_contrato,
            "escopo": c.escopo,
            "data": c.data_faturamento_protocolo,
            "valor": round(c.valor_protocolo or 0, 2),
            "tipo": "Protocolo"
        })

    # -------------------------------
    # Aprovações
    contratos_conclusao = Contrato.query.filter(
        Contrato.status_conclusao == True,
        Contrato.data_faturamento_conclusao != None,
        extract('year', Contrato.data_faturamento_conclusao) == ano,
        extract('month', Contrato.data_faturamento_conclusao) == mes
    ).all()
    for c in contratos_conclusao:
        faturamentos.append({
            "cliente": c.cliente.nome,
            "contrato": c.numero_contrato,
            "escopo": c.escopo,
            "data": c.data_faturamento_conclusao,
            "valor": round(c.valor_conclusao or 0, 2),
            "tipo": "Conclusão"
        })

    # -------------------------------
    # Lista de anos disponíveis (opcional)
    anos_disponiveis = sorted({c.data_faturamento_assinatura.year for c in Contrato.query.all() if c.data_faturamento_assinatura})

    return render_template(
        'dashboard/grafico_barras_faturamento_diario_no_mes.html',
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
        faturamentos=faturamentos
    )