from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import asc, func, extract
from models import db, Movimentacao, NotaFiscal
from datetime import datetime


dados_rfb_dre_bp = Blueprint('dados_rfb_dre', __name__)

# ---------------------------------------------------------
# ------------------- DRE Fluxo ---------------------------
# ---------------------------------------------------------
@dados_rfb_dre_bp.route('/dre_fluxo')
def dre_fluxo():
    # Pega o ano da query string, se não informado usa o ano atual
    ano_selecionado = request.args.get('ano', datetime.now().year, type=int)
    
    # Lista de meses para o cabeçalho
    meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
             'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    

    # ==========================================================
    # Inicializa o dicionário de dados consolidados
    # ==========================================================
    dados_consolidados = {
        # Itens Descrição — por data de movimentação
        'faturamento_bruto_mensal': [0.0] * 12,
        'simples_nacional_mensal': [0.0] * 12,
        'taxa_de_captacao_spl_mensal': [0.0] * 12,
        'taxa_de_captacao_gpm_mensal': [0.0] * 12,
        'fundo_de_reserva_mensal': [0.0] * 12,
        'despesas_administrativas_descricao_mensal': [0.0] * 12,

        # Itens Descrição — por competência
        'simples_nacional_por_competencia': [0.0] * 12,
        'taxa_de_captacao_spl_por_competencia': [0.0] * 12,
        'taxa_de_captacao_gpm_por_competencia': [0.0] * 12,
        'fundo_de_reserva_por_competencia': [0.0] * 12,
        'despesas_administrativas_descricao_por_competencia': [0.0] * 12,

        # Itens Contas — por data de movimentação
        'faturamento_liquido_mensal': [0.0] * 12,
        'pro_labore_contas_mensal': [0.0] * 12,
        'despesas_administrativas_contas_mensal': [0.0] * 12,

        # Itens Contas — por competência
        'pro_labore_contas_por_competencia': [0.0] * 12,
        'despesas_administrativas_contas_por_competencia': [0.0] * 12,
    }


    # ==========================================================
    # Função auxiliar para preencher os dados mensais
    # ==========================================================
    def processar_resultado(query_result, campo_destino):
        """Processa resultados mensais e armazena no dicionário."""
        for resultado in query_result:
            try:
                mes = int(float(resultado.mes))
                total = float(resultado.total) if resultado.total else 0.0
                if 1 <= mes <= 12:
                    dados_consolidados[campo_destino][mes - 1] = total
            except (ValueError, TypeError) as e:
                print(f"Erro ao processar resultado para {campo_destino}: {e}")


    # Queries e processamento
    try:
        # ==========================================================
        # CONSULTAS — POR DATA DE MOVIMENTAÇÃO
        # ==========================================================

        # --- Faturamento Bruto
        faturamento_bruto_query = db.session.query(
            extract('month', Movimentacao.data).label('mes'),
            func.sum(Movimentacao.valor).label('total')
        ).filter(
            extract('year', Movimentacao.data) == ano_selecionado,
            Movimentacao.operacao == 'Entrada',
            Movimentacao.movimentacao_tipo == 'Receita'
        ).group_by(extract('month', Movimentacao.data)).all()

        processar_resultado(faturamento_bruto_query, 'faturamento_bruto_mensal')


        # --- Simples Nacional
        simples_nacional_query = db.session.query(
            extract('month', Movimentacao.data).label('mes'),
            func.sum(Movimentacao.valor).label('total')
        ).filter(
            extract('year', Movimentacao.data) == ano_selecionado,
            Movimentacao.operacao == 'Saída',
            Movimentacao.movimentacao_categoria == 'Simples Nacional',
            Movimentacao.movimentacao_tipo == 'Despesa',
            Movimentacao.status_pagamento == 'Pago'
        ).group_by(extract('month', Movimentacao.data)).all()

        processar_resultado(simples_nacional_query, 'simples_nacional_mensal')


        # --- Taxa de Captação SPL
        taxa_spl_query = db.session.query(
            extract('month', Movimentacao.data).label('mes'),
            func.sum(Movimentacao.valor).label('total')
        ).filter(
            extract('year', Movimentacao.data) == ano_selecionado,
            Movimentacao.operacao == 'Saída',
            Movimentacao.movimentacao_categoria == 'Taxa de Captação SPL',
            Movimentacao.status_pagamento == 'Pago'
        ).group_by(extract('month', Movimentacao.data)).all()

        processar_resultado(taxa_spl_query, 'taxa_de_captacao_spl_mensal')


        # --- Taxa de Captação GPM
        taxa_gpm_query = db.session.query(
            extract('month', Movimentacao.data).label('mes'),
            func.sum(Movimentacao.valor).label('total')
        ).filter(
            extract('year', Movimentacao.data) == ano_selecionado,
            Movimentacao.operacao == 'Saída',
            Movimentacao.movimentacao_categoria == 'Taxa de Captação GPM',
            Movimentacao.status_pagamento == 'Pago'
        ).group_by(extract('month', Movimentacao.data)).all()

        processar_resultado(taxa_gpm_query, 'taxa_de_captacao_gpm_mensal')


        # --- Fundo de Reserva
        fundo_reserva_query = db.session.query(
            extract('month', Movimentacao.data).label('mes'),
            func.sum(Movimentacao.valor).label('total')
        ).filter(
            extract('year', Movimentacao.data) == ano_selecionado,
            Movimentacao.operacao == 'Saída',
            Movimentacao.movimentacao_categoria == 'Fundo de Reserva',
            Movimentacao.status_pagamento == 'Pago'
        ).group_by(extract('month', Movimentacao.data)).all()

        processar_resultado(fundo_reserva_query, 'fundo_de_reserva_mensal')


        # --- Despesas Administrativas (por data)
        despesas_admin_mensal_query = db.session.query(
            extract('month', Movimentacao.data).label('mes'),
            func.sum(Movimentacao.valor).label('total')
        ).filter(
            extract('year', Movimentacao.data) == ano_selecionado,
            Movimentacao.operacao == 'Saída',
            Movimentacao.movimentacao_tipo == 'Despesa',
            Movimentacao.status_pagamento == 'Pago'
        ).group_by(extract('month', Movimentacao.data)).all()

        processar_resultado(despesas_admin_mensal_query, 'despesas_administrativas_descricao_mensal')


        # ==========================================================
        # CONSULTAS — POR COMPETÊNCIA
        # ==========================================================

        # --- Simples Nacional
        simples_nacional_comp_query = db.session.query(
            Movimentacao.mes.label('mes'),
            func.sum(Movimentacao.valor).label('total')
        ).filter(
            Movimentacao.ano == ano_selecionado,
            Movimentacao.operacao == 'Saída',
            Movimentacao.movimentacao_categoria == 'Simples Nacional',
            Movimentacao.status_pagamento == 'Pago'
        ).group_by(Movimentacao.mes).order_by(Movimentacao.mes).all()

        processar_resultado(simples_nacional_comp_query, 'simples_nacional_por_competencia')


        # --- Taxa de Captação SPL
        taxa_spl_comp_query = db.session.query(
            Movimentacao.mes.label('mes'),
            func.sum(Movimentacao.valor).label('total')
        ).filter(
            Movimentacao.ano == ano_selecionado,
            Movimentacao.operacao == 'Saída',
            Movimentacao.movimentacao_categoria == 'Taxa de Captação SPL',
            Movimentacao.status_pagamento == 'Pago'
        ).group_by(Movimentacao.mes).order_by(Movimentacao.mes).all()

        processar_resultado(taxa_spl_comp_query, 'taxa_de_captacao_spl_por_competencia')


        # --- Taxa de Captação GPM
        taxa_gpm_comp_query = db.session.query(
            Movimentacao.mes.label('mes'),
            func.sum(Movimentacao.valor).label('total')
        ).filter(
            Movimentacao.ano == ano_selecionado,
            Movimentacao.operacao == 'Saída',
            Movimentacao.movimentacao_categoria == 'Taxa de Captação GPM',
            Movimentacao.status_pagamento == 'Pago'
        ).group_by(Movimentacao.mes).order_by(Movimentacao.mes).all()

        processar_resultado(taxa_gpm_comp_query, 'taxa_de_captacao_gpm_por_competencia')


        # --- Fundo de Reserva
        fundo_reserva_comp_query = db.session.query(
            Movimentacao.mes.label('mes'),
            func.sum(Movimentacao.valor).label('total')
        ).filter(
            Movimentacao.ano == ano_selecionado,
            Movimentacao.operacao == 'Saída',
            Movimentacao.movimentacao_categoria == 'Fundo de Reserva',
            Movimentacao.status_pagamento == 'Pago'
        ).group_by(Movimentacao.mes).order_by(Movimentacao.mes).all()

        processar_resultado(fundo_reserva_comp_query, 'fundo_de_reserva_por_competencia')


        # --- Despesas Administrativas (por competência, com subquery para deduzir Simples e Pro-labore)
        subquery_deducoes = db.session.query(
            Movimentacao.mes.label('mes'),
            func.sum(Movimentacao.valor).label('total')
        ).filter(
            Movimentacao.ano == ano_selecionado,
            Movimentacao.operacao == 'Saída',
            Movimentacao.movimentacao_tipo == 'Despesa',
            Movimentacao.movimentacao_categoria.in_(['Pro-labore', 'Simples Nacional']),
            Movimentacao.status_pagamento == 'Pago'
        ).group_by(Movimentacao.mes).subquery()

        despesas_admin_comp_query = db.session.query(
            Movimentacao.mes.label('mes'),
            (func.sum(Movimentacao.valor) - func.coalesce(subquery_deducoes.c.total, 0)).label('total')
        ).outerjoin(
            subquery_deducoes, subquery_deducoes.c.mes == Movimentacao.mes
        ).filter(
            Movimentacao.ano == ano_selecionado,
            Movimentacao.operacao == 'Saída',
            Movimentacao.movimentacao_tipo == 'Despesa',
            Movimentacao.status_pagamento == 'Pago'
        ).group_by(Movimentacao.mes, subquery_deducoes.c.total).order_by(Movimentacao.mes).all()

        processar_resultado(despesas_admin_comp_query, 'despesas_administrativas_descricao_por_competencia')
    
    except Exception as e:
        print(f"Erro nas queries: {e}")
    
    # Busca anos disponíveis
    anos_lista = [datetime.now().year]  # Valor padrão
    
    try:
        anos_set = set()
        
        # Anos das movimentações
        anos_mov = db.session.query(Movimentacao.ano).distinct().all()
        for ano in anos_mov:
            if ano[0]:
                anos_set.add(int(ano[0]))
        
        # Anos das NFs
        anos_nf = db.session.query(
            extract('year', NotaFiscal.data_emissao),
            extract('year', NotaFiscal.data_pagamento)
        ).all()
        
        for emissao, pagamento in anos_nf:
            if emissao:
                anos_set.add(int(float(emissao)))
            if pagamento:
                anos_set.add(int(float(pagamento)))
        
        if anos_set:
            anos_lista = sorted(list(anos_set), reverse=True)
            
    except Exception as e:
        print(f"Erro ao buscar anos: {e}")
    
    return render_template( 
        'dre/dre_fluxo.html',
        meses=meses,
        dados_consolidados=dados_consolidados,
        ano_selecionado=ano_selecionado,
        anos_disponiveis=anos_lista,
    )