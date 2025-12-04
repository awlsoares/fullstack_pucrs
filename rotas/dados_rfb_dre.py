from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import asc, func, extract
from models import db, Movimentacao, NotaFiscal, SaldoCaixaMensal
from datetime import datetime, date
import pprint

def debug(ano):
    # === DEBUG: listar movimentações do ano selecionado ===
    print(f"\n=== Movimentações encontradas para {ano} ===")
    movs_debug = Movimentacao.query.filter(
        extract('year', Movimentacao.data) == ano
    ).order_by(Movimentacao.data.asc()).all()

    for m in movs_debug:
        print(f"ID: {m.id} | Data: {m.data} | Valor: {m.valor} | "
            f"Tipo: {m.movimentacao_tipo} | Operação: {m.operacao} | "
            f"Status: {m.status_pagamento}")
    print("=== Fim da listagem ===\n")

    print("---------- Ano Atual - rfb_consolidado: ", datetime.now().year)

dados_rfb_dre_bp = Blueprint('dados_rfb_dre', __name__)

# ---------------------------------------------------------
# --------------- RFB Consolidado -------------------------
# ---------------------------------------------------------
@dados_rfb_dre_bp.route('/rfb_consolidado')
def rfb_consolidado():
    # Pega o ano da query string, se não informado usa o ano atual
    ano_selecionado = request.args.get('ano', datetime.now().year, type=int)

    # debug(ano_selecionado)
    
    # Lista de meses para o cabeçalho
    meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
             'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    
    # Inicializa os dados consolidados
    dados_consolidados = {
        'despesas': [0.0] * 12,
        'lucro_spl': [0.0] * 12,
        'lucro_gpm': [0.0] * 12,
        'nf_emitidas': [0.0] * 12,
        'nf_recebidas': [0.0] * 12,
        'investimento_reserva': [0.0] * 12,
        #  'caixa_emergencia': [0.0] * 12 (VERIFICAR SE É REALMENTE NECESSÁRIO)
    }
    
    def processar_resultado(query_result, campo_destino):
        """Função auxiliar para processar resultados das queries"""
        for resultado in query_result:
            try:
                mes = int(float(resultado.mes))  # Dupla conversão para garantir
                total = float(resultado.total) if resultado.total else 0.0
                
                if 1 <= mes <= 12:  # Validação adicional
                    mes_index = mes - 1

                    if campo_destino == 'investimento_reserva':
                        if mes != 1:
                            mes_index -= 1
                        else:
                            mes_index = 11

                    dados_consolidados[campo_destino][mes_index] = total
                    
            except (ValueError, TypeError) as e:
                print(f"Erro ao processar resultado: {e}")
                continue
    
    # Queries e processamento
    try:
        # Despesas
        despesas_query = db.session.query(
            extract('month', Movimentacao.data).label('mes'),
            func.sum(Movimentacao.valor).label('total')
        ).filter(
            extract('year', Movimentacao.data) == ano_selecionado,
            Movimentacao.operacao == 'Saída',
            (Movimentacao.movimentacao_tipo == 'Despesa'),
            Movimentacao.status_pagamento == 'Pago'
        ).group_by(extract('month', Movimentacao.data)).all()

        processar_resultado(despesas_query, 'despesas')
        
        # Lucro SPL
        lucro_spl_query = db.session.query(
            extract('month', Movimentacao.data).label('mes'),
            func.sum(Movimentacao.valor).label('total')
        ).filter(
            extract('year', Movimentacao.data) == ano_selecionado,
            Movimentacao.operacao == 'Saída',
            Movimentacao.movimentacao_tipo == 'Distribuição de Lucros',
            Movimentacao.movimentacao_categoria == 'SPL',
            Movimentacao.status_pagamento == 'Pago'
        ).group_by(extract('month', Movimentacao.data)).all()
        
        processar_resultado(lucro_spl_query, 'lucro_spl')
        
        # Lucro GPM
        lucro_gpm_query = db.session.query(
            extract('month', Movimentacao.data).label('mes'),
            func.sum(Movimentacao.valor).label('total')
        ).filter(
            extract('year', Movimentacao.data) == ano_selecionado,
            Movimentacao.operacao == 'Saída',
            Movimentacao.movimentacao_tipo == 'Distribuição de Lucros',
            Movimentacao.movimentacao_categoria == 'GPM',
            Movimentacao.status_pagamento == 'Pago'
        ).group_by(extract('month', Movimentacao.data)).all()
        
        processar_resultado(lucro_gpm_query, 'lucro_gpm')

        # Investimento Reservas
        investimento_reserva_query = db.session.query(
            extract('month', Movimentacao.data).label('mes'),
            func.sum(Movimentacao.valor).label('total')
        ).filter(
            extract('year', Movimentacao.data) == ano_selecionado,
            Movimentacao.operacao == 'Saída',
            Movimentacao.movimentacao_tipo == 'Reserva de Caixa',
            Movimentacao.movimentacao_categoria == 'Reserva de Caixa'
        ).group_by(extract('month', Movimentacao.data)).all()
        
        processar_resultado(investimento_reserva_query, 'investimento_reserva')
        
        # NFs Emitidas
        nf_emitidas_query = db.session.query(
            extract('month', NotaFiscal.data_emissao).label('mes'),
            func.sum(NotaFiscal.valor_bruto).label('total')
        ).filter(
            extract('year', NotaFiscal.data_emissao) == ano_selecionado
        ).group_by(extract('month', NotaFiscal.data_emissao)).all()
        
        processar_resultado(nf_emitidas_query, 'nf_emitidas')

        # NFs Recebidas
        nf_recebidas_query = db.session.query(
            extract('month', NotaFiscal.data_pagamento).label('mes'),
            func.sum(NotaFiscal.valor_liquido).label('total')
        ).filter(
            extract('year', NotaFiscal.data_pagamento) == ano_selecionado
        ).group_by(extract('month', NotaFiscal.data_pagamento)).all()
        
        processar_resultado(nf_recebidas_query, 'nf_recebidas')
        
        
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
        'dre/rfb_consolidado.html',
        meses=meses,
        dados_consolidados=dados_consolidados,
        ano_selecionado=ano_selecionado,
        anos_disponiveis=anos_lista,
    )


# ---------------------------------------------------------
# ------------------- DRE Fluxo ---------------------------
# ---------------------------------------------------------
@dados_rfb_dre_bp.route('/dre_fluxo')
def dre_fluxo():

    # Valor para inicializar o sistema (Saldo em 31/12/2024)
    # saldo_mes_anterior_inicial = float(2661.12)

    # Pega o ano da query string, se não informado usa o ano atual
    ano_selecionado = request.args.get('ano', datetime.now().year, type=int)
    
    # Lista de meses para o cabeçalho
    meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
             'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    
    # Inicializa os dados consolidados
    dados_consolidados = {
        # Itens DRE - Competência 
        'faturamento_bruto': [0.0] * 12,
        'simples_nacional_dre': [0.0] * 12,
        'taxa_de_captacao_spl_dre': [0.0] * 12,
        'taxa_de_captacao_gpm_dre': [0.0] * 12,
        'fundo_de_reserva_dre': [0.0] * 12,
        'receita_liquida_dre': [0.0] * 12,
        'despesas_administrativas_dre': [0.0] * 12,
        'resultado_liquido_dre': [0.0] * 12,

        # Itens Fluxo de Caixa
        'faturamento_liquido': [0.0] * 12,
        'pro_labore_fluxo': [0.0] * 12,
        'simples_nacional_fluxo': [0.0] * 12,
        'despesas_administrativas_fluxo': [0.0] * 12,
        'taxa_de_captacao_spl_fluxo': [0.0] * 12,
        'taxa_de_captacao_gpm_fluxo': [0.0] * 12,
        'total_despesas_fluxo': [0.0] * 12,
        'saldo_caixa_fluxo': [0.0] * 12,


        'saldo_caixa_mes_anterior_fluxo': [0.0] * 12,
        'caixa_antes_reserva_fluxo': [0.0] * 12,
        'fundo_de_reserva_fluxo': [0.0] * 12,
        'caixa_depois_reserva_fluxo': [0.0] * 12,
        'lucro_spl_fluxo': [0.0] * 12,
        'lucro_gpm_fluxo': [0.0] * 12,
        'saldo_final_caixa_fluxo': [0.0] * 12,
    }
    
    def processar_resultado(query_result, campo_destino):
        """Função auxiliar para processar resultados das queries"""
        for resultado in query_result:
            try:
                mes = int(float(resultado.mes))  # Dupla conversão para garantir
                total = float(resultado.total) if resultado.total else 0.0
                
                if 1 <= mes <= 12:  # Validação adicional
                    mes_index = mes - 1

                    if campo_destino == 'investimento_reserva':
                        if mes != 1:
                            mes_index -= 1
                        else:
                            mes_index = 11

                    dados_consolidados[campo_destino][mes_index] = total
                    
            except (ValueError, TypeError) as e:
                print(f"Erro ao processar resultado: {e}")
                continue
    
    # Queries e processamento
    try:

        ''' ------------------------------------------------------------------------
        ###### ------------ ITENS DO DEMONSTRATIVO DE RESULTADOS ------------####### 
        ------------------------------------------------------------------------ ''' 
    
        # ---------------------------------------------------------
        # FATURAMENTO BRUTO — NFs Emitidas (por data da emissão)
        # ---------------------------------------------------------
        faturamento_bruto_query = db.session.query(
            extract('month', NotaFiscal.data_emissao).label('mes'),
            func.sum(NotaFiscal.valor_bruto).label('total')
        ).filter(
            extract('year', NotaFiscal.data_emissao) == ano_selecionado
        ).group_by(extract('month', NotaFiscal.data_emissao)).all()
        
        processar_resultado(faturamento_bruto_query, 'faturamento_bruto')     


        # ---------------------------------------------------------
        # SIMPLES NACIONAL (DRE) — usa competência
        # ---------------------------------------------------------
        simples_nacional_query = db.session.query(
            Movimentacao.mes.label('mes'),
            func.sum(Movimentacao.valor).label('total')
        ).filter(
            Movimentacao.ano == ano_selecionado,
            Movimentacao.operacao == 'Saída',
            Movimentacao.movimentacao_tipo == 'Despesa',
            Movimentacao.movimentacao_categoria == 'Simples Nacional',
            Movimentacao.status_pagamento == 'Pago'
        ).group_by(Movimentacao.mes).order_by(Movimentacao.mes).all()

        processar_resultado(simples_nacional_query, 'simples_nacional_dre')


        # ---------------------------------------------------------
        # TAXA DE CAPTAÇÃO SPL — usa competência
        # ---------------------------------------------------------
        taxa_captacao_spl_query = db.session.query(
            Movimentacao.mes.label('mes'),
            func.sum(Movimentacao.valor).label('total')
        ).filter(
            Movimentacao.ano == ano_selecionado,
            Movimentacao.operacao == 'Saída',
            Movimentacao.movimentacao_tipo == 'Taxa de Captação',
            Movimentacao.movimentacao_categoria == 'SPL',
            Movimentacao.status_pagamento == 'Pago'
        ).group_by(Movimentacao.mes).order_by(Movimentacao.mes).all()

        processar_resultado(taxa_captacao_spl_query, 'taxa_de_captacao_spl_dre')


        # ---------------------------------------------------------
        # TAXA DE CAPTAÇÃO GPM — usa competência
        # ---------------------------------------------------------
        taxa_captacao_gpm_query = db.session.query(
            Movimentacao.mes.label('mes'),
            func.sum(Movimentacao.valor).label('total')
        ).filter(
            Movimentacao.ano == ano_selecionado,
            Movimentacao.operacao == 'Saída',
            Movimentacao.movimentacao_tipo == 'Taxa de Captação',
            Movimentacao.movimentacao_categoria == 'GPM',
            Movimentacao.status_pagamento == 'Pago'
        ).group_by(Movimentacao.mes).order_by(Movimentacao.mes).all()

        processar_resultado(taxa_captacao_gpm_query, 'taxa_de_captacao_gpm_dre')


        # ---------------------------------------------------------
        # FUNDO DE RESERVA — usa competência
        # ---------------------------------------------------------
        fundo_reserva_query = db.session.query(
            Movimentacao.mes.label('mes'),
            func.sum(Movimentacao.valor).label('total')
        ).filter(
            Movimentacao.ano == ano_selecionado,
            Movimentacao.operacao == 'Saída',
            Movimentacao.movimentacao_tipo == 'Reserva de Caixa',
            Movimentacao.movimentacao_categoria == 'Reserva de Caixa',
            Movimentacao.status_pagamento == 'Pago'
        ).group_by(Movimentacao.mes).order_by(Movimentacao.mes).all()

        processar_resultado(fundo_reserva_query, 'fundo_de_reserva_dre')


        # ---------------------------------------------------------
        # RECEITA LÍQUIDA - DRE
        # ---------------------------------------------------------
        receita_liquida_mensal = []
        for i in range(12):
            faturamento = dados_consolidados['faturamento_bruto'][i]
            simples_nacional = dados_consolidados['simples_nacional_dre'][i]
            captacao_spl = dados_consolidados['taxa_de_captacao_spl_dre'][i]
            captacao_gpm = dados_consolidados['taxa_de_captacao_gpm_dre'][i]
            reserva = dados_consolidados['fundo_de_reserva_dre'][i]

            receita_liquida_mensal.append(faturamento - simples_nacional - captacao_spl - captacao_gpm - reserva)

        dados_consolidados['receita_liquida_dre'] = receita_liquida_mensal


        # ---------------------------------------------------------
        # DESPESAS ADMINISTRATIVAS - DRE — usa competência
        # ---------------------------------------------------------
        despesas_administrativas_dre_query = db.session.query(
            Movimentacao.mes.label('mes'),
            func.sum(Movimentacao.valor).label('total')
        ).filter(
            Movimentacao.ano == ano_selecionado,
            Movimentacao.operacao == 'Saída',
            Movimentacao.movimentacao_tipo == 'Despesa',
            Movimentacao.movimentacao_categoria != 'Simples Nacional',
            Movimentacao.status_pagamento == 'Pago'
        ).group_by(Movimentacao.mes).order_by(Movimentacao.mes).all()

        processar_resultado(despesas_administrativas_dre_query, 'despesas_administrativas_dre')


        # ---------------------------------------------------------
        # RESULTADO LÍQUIDO - DRE
        # ---------------------------------------------------------
        resultado_liquido_mensal = []
        for i in range(12):
            receita_liquida = dados_consolidados['receita_liquida_dre'][i]
            despesas_administrativas = dados_consolidados['despesas_administrativas_dre'][i]
            resultado_liquido_mensal.append(receita_liquida - despesas_administrativas)

        # print(resultado_liquido_mensal)
        dados_consolidados['resultado_liquido_dre'] = resultado_liquido_mensal


        ''' -------------------------------------------------------------------
        ######----------------- ITENS DO FLUXO DE CAIXA ----------------####### 
        ------------------------------------------------------------------- '''

        # ---------------------------------------------------------
        # 1. FATURAMENTO LÍQUIDO (RECEBIMENTO) — NFs Recebidas (por data de recebimento)
        # ---------------------------------------------------------
        faturamento_liquido_query = db.session.query(
            extract('month', NotaFiscal.data_pagamento).label('mes'),
            func.sum(NotaFiscal.valor_liquido).label('total')
        ).filter(
            extract('year', NotaFiscal.data_pagamento) == ano_selecionado,
            NotaFiscal.data_pagamento.isnot(None)
        ).group_by(extract('month', NotaFiscal.data_pagamento)).all()
        
        processar_resultado(faturamento_liquido_query, 'faturamento_liquido')


        # ---------------------------------------------------------
        # 2. PRO-LABORE — usa data da movimentação
        # ---------------------------------------------------------
        pro_labore_query = db.session.query(
            extract('month', Movimentacao.data).label('mes'),
            func.sum(Movimentacao.valor).label('total')
        ).filter(
            Movimentacao.ano == ano_selecionado,
            Movimentacao.operacao == 'Saída',
            Movimentacao.movimentacao_tipo == 'Despesa',
            Movimentacao.movimentacao_categoria == 'Pro-labore',
            Movimentacao.status_pagamento == 'Pago'
        ).group_by(extract('month', Movimentacao.data)).order_by(extract('month', Movimentacao.data)).all()

        processar_resultado(pro_labore_query, 'pro_labore_fluxo')


        # ------------------------------------------------------------
        # 3. SIMPLES NACIONAL (Fluxo de Caixa) — usa data da movimentação
        # ------------------------------------------------------------
        simples_nacional_fluxo_query = db.session.query(
            extract('month', Movimentacao.data).label('mes'),
            func.sum(Movimentacao.valor).label('total')
        ).filter(
            Movimentacao.ano == ano_selecionado,
            Movimentacao.operacao == 'Saída',
            Movimentacao.movimentacao_tipo == 'Despesa',
            Movimentacao.movimentacao_categoria == 'Simples Nacional',
            Movimentacao.status_pagamento == 'Pago'
        ).group_by(extract('month', Movimentacao.data)).order_by(extract('month', Movimentacao.data)).all()

        processar_resultado(simples_nacional_fluxo_query, 'simples_nacional_fluxo')

        
        # --------------------------------------------------------------------
        # 4. DESPESAS ADMINISTRATIVAS (FLuxo de Caixa) — usa data da movimentação
        # --------------------------------------------------------------------
        despesas_administrativas_fluxo_query = db.session.query(
            extract('month', Movimentacao.data).label('mes'),
            func.sum(Movimentacao.valor).label('total')
        ).filter(
            extract('year', Movimentacao.data) == ano_selecionado,
            Movimentacao.operacao == 'Saída',
            Movimentacao.movimentacao_tipo == 'Despesa',
            Movimentacao.movimentacao_categoria != 'Pro-labore',
            Movimentacao.movimentacao_categoria != 'Simples Nacional',
            Movimentacao.status_pagamento == 'Pago'
        ).group_by(extract('month', Movimentacao.data)).order_by(extract('month', Movimentacao.data)).all()

        processar_resultado(despesas_administrativas_fluxo_query, 'despesas_administrativas_fluxo')


        # ----------------------------------------------------------------
        # 5. TAXA DE CAPTAÇÃO SPL (Fluxo de Caixa) — usa data da movimentação
        # ----------------------------------------------------------------
        taxa_captacao_spl_fluxo_query = db.session.query(
            extract('month', Movimentacao.data).label('mes'),
            func.sum(Movimentacao.valor).label('total')
        ).filter(
            Movimentacao.ano == ano_selecionado,
            Movimentacao.operacao == 'Saída',
            Movimentacao.movimentacao_tipo == 'Taxa de Captação',
            Movimentacao.movimentacao_categoria == 'SPL',
            Movimentacao.status_pagamento == 'Pago'
        ).group_by(extract('month', Movimentacao.data)).order_by(extract('month', Movimentacao.data)).all()

        processar_resultado(taxa_captacao_spl_fluxo_query, 'taxa_de_captacao_spl_fluxo')


        # ------------------------------------------------------------------
        # 5. TAXA DE CAPTAÇÃO GPM — (Fluxo de Caixa) — usa data da movimentação
        # -----------------------------------------------------------------
        taxa_captacao_gpm_fluxo_query = db.session.query(
            extract('month', Movimentacao.data).label('mes'),
            func.sum(Movimentacao.valor).label('total')
        ).filter(
            Movimentacao.ano == ano_selecionado,
            Movimentacao.operacao == 'Saída',
            Movimentacao.movimentacao_tipo == 'Taxa de Captação',
            Movimentacao.movimentacao_categoria == 'GPM',
            Movimentacao.status_pagamento == 'Pago'
        ).group_by(extract('month', Movimentacao.data)).order_by(extract('month', Movimentacao.data)).all()

        processar_resultado(taxa_captacao_gpm_fluxo_query, 'taxa_de_captacao_gpm_fluxo')


        # ---------------------------------------------------------
        # 6. TOTAL DAS DESPESAS - (Fluxo de Caixa)
        # ---------------------------------------------------------
        total_despesa_mensal = []
        for i in range(12):
            pro_labore = dados_consolidados['pro_labore_fluxo'][i]
            simples_nacional = dados_consolidados['simples_nacional_fluxo'][i]
            captacao = dados_consolidados['taxa_de_captacao_spl_fluxo'][i] + dados_consolidados['taxa_de_captacao_gpm_fluxo'][i]
            despesas_administrativas = dados_consolidados['despesas_administrativas_fluxo'][i]

            total_despesa_mensal.append(pro_labore + simples_nacional + captacao + despesas_administrativas)

        dados_consolidados['total_despesas_fluxo'] = total_despesa_mensal

        # ---------------------------------------------------------
        # 7. SALDO DE CAIXA - (Fluxo de Caixa)
        # ---------------------------------------------------------
        saldo_caixa_mensal = []
        for i in range(12):
            recebimento = dados_consolidados['faturamento_liquido'][i]
            total_despesas = dados_consolidados['total_despesas_fluxo'][i]

            saldo_caixa_mensal.append(recebimento - total_despesas)

        dados_consolidados['saldo_caixa_fluxo'] = saldo_caixa_mensal


        # ---------------------------------------------------------
        # 12. DISTRIBUIÇÃO DE LUCROS SPL — usa data da movimentação
        # ---------------------------------------------------------
        lucro_spl_fluxo_query = db.session.query(
            extract('month', Movimentacao.data).label('mes'),
            func.sum(Movimentacao.valor).label('total')
        ).filter(
            extract('year', Movimentacao.data) == ano_selecionado,
            Movimentacao.operacao == 'Saída',
            Movimentacao.movimentacao_tipo == 'Distribuição de Lucros',
            Movimentacao.movimentacao_categoria == 'SPL',
            Movimentacao.status_pagamento == 'Pago'
        ).group_by(extract('month', Movimentacao.data)).order_by(extract('month', Movimentacao.data)).all()

        processar_resultado(lucro_spl_fluxo_query, 'lucro_spl_fluxo')


        # ---------------------------------------------------------
        # 13. DISTRIBUIÇÃO DE LUCROS GPM — usa data da movimentação
        # ---------------------------------------------------------
        lucro_gpm_fluxo_query = db.session.query(
            extract('month', Movimentacao.data).label('mes'),
            func.sum(Movimentacao.valor).label('total')
        ).filter(
            extract('year', Movimentacao.data) == ano_selecionado,
            Movimentacao.operacao == 'Saída',
            Movimentacao.movimentacao_tipo == 'Distribuição de Lucros',
            Movimentacao.movimentacao_categoria == 'GPM',
            Movimentacao.status_pagamento == 'Pago'
        ).group_by(extract('month', Movimentacao.data)).order_by(extract('month', Movimentacao.data)).all()

        processar_resultado(lucro_gpm_fluxo_query, 'lucro_gpm_fluxo')


        # ---------------------------------------------------------
        # 8, 9, 10, 11 e 14. SALDO DE CAIXA DO FLUXO - Encadeamento mensal com update no banco
        # ---------------------------------------------------------
        saldo_caixa_mes_anterior_fluxo = []
        saldo_final_caixa_fluxo = []

        for i in range(12):
            mes_atual = i + 1  # Janeiro = 1, Fevereiro = 2, etc.

            # -----------------------------
            # 8. SALDO DO MÊS ANTERIOR
            # -----------------------------
            if i == 0:
                # Para janeiro, busca saldo final de dezembro do ano anterior no banco
                saldo_inicial = float(
                    db.session.query(SaldoCaixaMensal.saldo_final)
                    .filter_by(ano=ano_selecionado - 1, mes=12)
                    .scalar()
                ) or 0
            else:
                # Para demais meses, saldo inicial = saldo final do mês anterior
                saldo_inicial = saldo_final_caixa_fluxo[i - 1]

            saldo_caixa_mes_anterior_fluxo.append(saldo_inicial)

            # -----------------------------
            # 9. CAIXA ANTES DA RESERVA
            # -----------------------------
            caixa_antes_reserva = saldo_inicial + dados_consolidados['saldo_caixa_fluxo'][i]
            print(
                f">>>>>> i: {i} ---> Saldo Inicial: R$ {saldo_inicial} ---> Saldo Caixa Fluxo: R$ {dados_consolidados['saldo_caixa_fluxo'][i]} ---> Soma: {caixa_antes_reserva}")

            # -----------------------------
            # 10. FUNDO DE RESERVA (10% ou valor existente)
            # -----------------------------
            # if 'fundo_de_reserva_fluxo' in dados_consolidados and len(dados_consolidados['fundo_de_reserva_fluxo']) == 12:
            #     fundo_reserva = dados_consolidados['fundo_de_reserva_fluxo'][i]
            # else:
            #     fundo_reserva = caixa_antes_reserva * 0.10
            fundo_reserva = dados_consolidados['fundo_de_reserva_dre'][i]
            dados_consolidados['fundo_de_reserva_fluxo'][i] = fundo_reserva

            # -----------------------------
            # 11. CAIXA DEPOIS DA RESERVA
            # -----------------------------
            caixa_depois_reserva = caixa_antes_reserva - fundo_reserva

            # -----------------------------
            # 12 e 13. Lucro SPL e GPM foram calculados fora deste loop
            # -----------------------------

            # -----------------------------
            # 14. SALDO FINAL DE CAIXA
            # -----------------------------
            saldo_final = caixa_depois_reserva - (dados_consolidados['lucro_spl_fluxo'][i] + dados_consolidados['lucro_gpm_fluxo'][i])
            saldo_final_caixa_fluxo.append(saldo_final)

            # -----------------------------
            # Atualiza ou cria registro no banco
            # -----------------------------
            registro = db.session.query(SaldoCaixaMensal).filter_by(
                ano=ano_selecionado, mes=mes_atual
            ).first()

            if registro:
                registro.saldo_final = saldo_final
                registro.criado_em = date.today()
            else:
                registro = SaldoCaixaMensal(
                    ano=ano_selecionado,
                    mes=mes_atual,
                    saldo_final=saldo_final,
                    criado_em=date.today()
                )
                db.session.add(registro)

            db.session.commit()  # garante que o próximo mês use este saldo atualizado

        # ---------------------------------------------------------
        # Atualiza o dicionário consolidado
        # ---------------------------------------------------------
        dados_consolidados['saldo_caixa_mes_anterior_fluxo'] = saldo_caixa_mes_anterior_fluxo
        dados_consolidados['fundo_de_reserva_fluxo'] = [dados_consolidados.get('fundo_de_reserva_fluxo', [0]*12)[i] for i in range(12)]
        dados_consolidados['caixa_antes_reserva_fluxo'] = [saldo_caixa_mes_anterior_fluxo[i] + dados_consolidados['saldo_caixa_fluxo'][i] for i in range(12)]
        dados_consolidados['caixa_depois_reserva_fluxo'] = [dados_consolidados['caixa_antes_reserva_fluxo'][i] - dados_consolidados['fundo_de_reserva_fluxo'][i] for i in range(12)]
        dados_consolidados['saldo_final_caixa_fluxo'] = saldo_final_caixa_fluxo


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
    
    pprint.pprint(dados_consolidados)
    
    return render_template( 
        'dre/dre_fluxo.html',
        meses=meses,
        dados_consolidados=dados_consolidados,
        ano_selecionado=ano_selecionado,
        anos_disponiveis=anos_lista,
    )
