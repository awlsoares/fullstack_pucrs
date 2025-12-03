from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import asc, event
from models import db, Movimentacao, update_mes_ano
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

movimentacoes_bp = Blueprint('movimentacoes', __name__)

def lista_categorias():
    lista_categorias = [
        "Alimentação", "Aluguel", "Anuidade", "Cartão de Crédito", "Certificado Digital", "Contabilidade",
        "Energia", "GPM", "Imposto", "Internet", "Investimento", "Juros", "NF Atrasada", "Prestação de Serviço",
        "Pro-labore", "Receita", "Rendimento", "Reserva de Caixa", "Resgate de Investimento", "Simples Nacional","SPL",
        "Transferência"    
    ]
    return lista_categorias

def lista_tipos():
    lista_tipos = [
        "Despesa", "Distribuição de Lucros", "Investimento", "Juros", "Receita", "Rendimento", "Reserva de Caixa",
        "Resgate", "Taxa de Captação", "Transferência"
    ]
    return lista_tipos

def processar_dados_form():
    try:
        #data_cadastro = datetime.now().date()
        operacao = request.form['operacao']
        data = request.form['data']
        competencia = request.form['competencia']
        descricao = request.form.get('descricao', '')
        forma_de_pagamento = request.form['forma_de_pagamento']
        status_pagamento = request.form['status_pagamento']
        movimentacao_tipo = request.form['movimentacao_tipo']
        movimentacao_categoria = request.form['movimentacao_categoria']
        valor = request.form['valor']
        observacao = request.form.get('observacao', '')

        ano, mes = competencia.split('-')
        mes = int(mes)
        ano = int(ano)

        valor_float = float(valor)
        if valor_float < 0:
            raise ValueError('Valor não pode ser negativo')

        # data_cadastro_obj = datetime.strptime(data_cadastro, '%Y-%m-%d').date()
        # data_cadastro_obj = datetime.now().date()
        data_obj = datetime.strptime(data, '%Y-%m-%d').date()

        return {
            #'data_cadastro': data_cadastro_obj,
            'operacao': operacao, #.lower(),
            'data': data_obj,
            'descricao': descricao,
            'forma_de_pagamento': forma_de_pagamento,
            'status_pagamento': status_pagamento,
            'mes': mes,
            'ano': ano,
            'movimentacao_tipo': movimentacao_tipo,
            'movimentacao_categoria': movimentacao_categoria,
            'valor': valor_float,
            'observacao': observacao
        }

    except Exception as e:
        raise e

def atualiza_caixa(data):
    pass

@movimentacoes_bp.route('/nova_movimentacao', methods=['GET', 'POST'])
def nova_movimentacao():
    if request.method == 'POST':
        try:
            dados = processar_dados_form()
            print("Movimentação a ser cadastrada? \n", dados)
            nova_mov = Movimentacao(**dados)

            db.session.add(nova_mov)
            db.session.commit()
            flash('Movimentação cadastrada com sucesso!', 'success')
            return redirect(url_for('movimentacoes.listar_movimentacoes'))

        except Exception as e:
            flash(f'Erro ao cadastrar movimentação: {str(e)}', 'danger')
            db.session.rollback()

    return render_template('movimentacoes/movimentacao_cadastro.html')

@movimentacoes_bp.route('/nova_movimentacao_parcelada', methods=['GET', 'POST'])
def nova_movimentacao_parcelada():
    if request.method == 'POST':
        try:
            parcelas = int(request.form['parcelas'])
            operacao = request.form['operacao']
            data = request.form['data']
            competencia = request.form['competencia']
            descricao = request.form.get('descricao', '')
            forma_de_pagamento = request.form['forma_de_pagamento']
            # status_pagamento = request.form['status_pagamento']
            movimentacao_tipo = request.form['movimentacao_tipo']
            movimentacao_categoria = request.form['movimentacao_categoria']
            valor = round(((float(request.form['valor']))/parcelas), 2)
            print(f"VAlor do request: {request.form['valor']}, Valor Float: {float(request.form['valor'])}, Float Parcelado: {(float(request.form['valor']))/parcelas} Parcela Arredondada: {round((float(request.form['valor']))/parcelas, 2)}")
            observacao = request.form.get('observacao', '')

            ano, mes = competencia.split('-')
            mes = int(mes)
            ano = int(ano)

            valor_float = float(valor)
            if valor_float < 0:
                raise ValueError('Valor não pode ser negativo')

            data_inicial = datetime.strptime(data, '%Y-%m-%d').date()
            nova_data = data_inicial
            descricao_original = descricao

            for parcela in range(1, parcelas + 1):
                
                # Ajusta competência (mes/ano) conforme diferença original
                # Exemplo: se mov.data era 05/01/2024, mas competência era 12/2023
                diferenca_meses = (ano - data_inicial.year) * 12 + (mes - data_inicial.month)
                competencia_ajustada = nova_data + relativedelta(months=diferenca_meses)

                nova_mov = Movimentacao(
                    descricao = descricao_original + f" ({parcela}/{parcelas})",
                    valor = valor,
                    operacao = operacao,
                    movimentacao_tipo = movimentacao_tipo,
                    movimentacao_categoria = movimentacao_categoria,
                    forma_de_pagamento = forma_de_pagamento,
                    status_pagamento = 'Aberto',
                    data = nova_data,
                    mes = competencia_ajustada.month,
                    ano = competencia_ajustada.year,
                    observacao = f"Parcela: ({parcela}/{parcelas})"
                )

                db.session.add(nova_mov)
                nova_data = data_inicial + relativedelta(months=parcela)

            db.session.commit()
            flash(f"Movimentação parcelada criada com sucesso ({parcelas}x de R$ {valor:.2f}).", "success")
            return redirect(url_for('movimentacoes.listar_movimentacoes'))

        except Exception as e:
            flash(f'Erro ao cadastrar movimentação: {str(e)}', 'danger')
            db.session.rollback()

    return render_template('movimentacoes/movimentacao_cadastro_parcelada.html')

@movimentacoes_bp.route('/listar_movimentacoes')
def listar_movimentacoes():
    categorias = lista_categorias()
    tipos = lista_tipos()

    hoje = date.today()
    try:
        # page = request.args.get('page', 1, type=int)
        query = Movimentacao.query

        # filtros (se tiver)
        tipo = request.args.get('tipo')
        categoria = request.args.get('categoria')
        ano = request.args.get('ano', type=int)
        mes = request.args.get('mes', type=int)
        status = request.args.get('status')

        if tipo:
            query = query.filter(Movimentacao.movimentacao_tipo == tipo)
        if categoria:
            query = query.filter(Movimentacao.movimentacao_categoria == categoria)
        if ano:
            query = query.filter(Movimentacao.ano == ano)
        if mes:
            query = query.filter(Movimentacao.mes == mes)
        if status:
            query = query.filter(Movimentacao.status_pagamento == status)

        movimentacoes = query.order_by(asc(Movimentacao.data)) #.paginate(page=page, per_page=10)

        # totais filtrados
        total_entradas = query.with_entities(db.func.sum(Movimentacao.valor))\
            .filter(Movimentacao.operacao == 'Entrada').scalar() or 0
        total_saidas = query.with_entities(db.func.sum(Movimentacao.valor))\
            .filter(Movimentacao.operacao == 'Saida').scalar() or 0
        saldo = total_entradas - total_saidas

        print("Totais: ", total_entradas, total_saidas, saldo)
        return render_template(
            'movimentacoes/movimentacoes_lista.html',
            movimentacoes=movimentacoes,
            tipos = tipos,
            categorias = categorias,
            total_entradas=total_entradas,
            total_saidas=total_saidas,
            saldo=saldo,
            hoje = hoje
        )

    except Exception as e:
        flash(f'Erro ao carregar movimentacoes: {str(e)}', 'danger')
        return render_template(
            'movimentacoes/movimentacoes_lista.html',
            movimentacoes=[],
            tipos = tipos,
            categorias = categorias,
            total_receitas=0,
            total_despesas=0,
            saldo=0
        )

@movimentacoes_bp.route('/editar_movimentacao/<int:id>', methods=['GET', 'POST'])
def editar_movimentacao(id):
    movimentacao = Movimentacao.query.get_or_404(id)

    if request.method == 'POST':
        try:
            dados = processar_dados_form()
            for chave, valor in dados.items():
                setattr(movimentacao, chave, valor)

            db.session.commit()
            flash('Movimentação atualizada com sucesso!', 'success')
            return redirect(url_for('movimentacoes.listar_movimentacoes'))

        except Exception as e:
            flash(f'Erro ao atualizar movimentação: {str(e)}', 'danger')
            db.session.rollback()
    
    return render_template('movimentacoes/movimentacao_cadastro.html', movimentacao=movimentacao)

@movimentacoes_bp.route('/deletar_movimentacao/<int:id>', methods=['POST'])
def deletar_movimentacao(id):
    try:
        movimentacao = Movimentacao.query.get_or_404(id)
        db.session.delete(movimentacao)
        db.session.commit()
        flash('Movimentação deletada com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao deletar movimentação: {str(e)}', 'danger')
        db.session.rollback()
    
    return redirect(url_for('movimentacoes.listar_movimentacoes'))


@movimentacoes_bp.route('/repetir_movimentacao/<int:id>', methods=['POST'])
def repetir_movimentacao(id):
    mov = Movimentacao.query.get_or_404(id)
    qtd = int(request.form.get('qtd-repeticoes', 1))
    data_inicial = datetime.strptime(request.form.get('data-repeticao'), "%Y-%m-%d").date()

    data_original = mov.data
    mes_original = mov.mes
    ano_original = mov.ano

    for i in range(qtd):
        nova_data = data_inicial + relativedelta(months=i)

        # Ajusta competência (mes/ano) conforme diferença original
        # Exemplo: se mov.data era 05/01/2024, mas competência era 12/2023
        diferenca_meses = (ano_original - data_original.year) * 12 + (mes_original - data_original.month)
        competencia_ajustada = nova_data + relativedelta(months=diferenca_meses)

        nova_mov = Movimentacao(
            descricao=mov.descricao,
            valor=mov.valor,
            operacao=mov.operacao,
            movimentacao_tipo=mov.movimentacao_tipo,
            movimentacao_categoria=mov.movimentacao_categoria,
            forma_de_pagamento=mov.forma_de_pagamento,
            status_pagamento='Aberto',
            data=nova_data,
            mes=competencia_ajustada.month,
            ano=competencia_ajustada.year
        )

        db.session.add(nova_mov)

    db.session.commit()
    flash(f'{qtd} movimentação(ões) duplicada(s) com sucesso!', 'success')
    return redirect(url_for('movimentacoes.listar_movimentacoes'))


# --- Função auxiliar temporária para desativar o event listener ---
def _temporariamente_desativar_listener():
    event.remove(Movimentacao.data, 'set', update_mes_ano)

def _reativar_listener():
    event.listen(Movimentacao.data, 'set', update_mes_ano)

@movimentacoes_bp.route('/movimentacao/atualizar_status', methods=['POST'])
def atualizar_status_movimentacao():
    try:
        dados = request.get_json()
        mov_id = dados.get('mov_id')
        data_usuario = dados.get('data_usuario')
        novo_status = dados.get('novo_status')

        if not mov_id or not data_usuario or not novo_status:
            return jsonify(success=False, message="Dados incompletos recebidos."), 400

        mov = Movimentacao.query.get(mov_id)
        if not mov:
            return jsonify(success=False, message="Movimentação não encontrada."), 404

        # Converte a data enviada (yyyy-mm-dd)
        data_formatada = datetime.strptime(data_usuario, "%Y-%m-%d").date()

        # Desativa temporariamente o listener
        _temporariamente_desativar_listener()

        # Atualiza apenas os campos relevantes
        mov.data = data_formatada
        mov.status_pagamento = novo_status

        db.session.commit()

        # Reativa o listener após a operação
        _reativar_listener()

        # Atualiza o Saldo Final do Caixa
        atualiza_caixa(data_formatada)

        return jsonify(success=True, message="Movimentação atualizada com sucesso!")

    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message=f"Erro ao atualizar movimentação: {str(e)}"), 500
