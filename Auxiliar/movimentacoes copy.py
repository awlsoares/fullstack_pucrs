from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import asc
from models import db, Movimentacao
from datetime import datetime

movimentacoes_bp = Blueprint('movimentacoes', __name__)

def processar_dados_form():
    print("=== INICIO processar_dados_form ===")

    try:
        print("1. Capturando dados do form...")
        data_cadastro = request.form['data_cadastro']
        print(f"data_cadastro: {data_cadastro}")

        operacao = request.form['operacao']
        print(f"operacao: {operacao}")

        data = request.form['data']
        print(f"data: {data}")

        competencia = request.form['competencia']
        print(f"competencia: {competencia}")

        descricao = request.form.get('descricao', '')
        forma_de_pagamento = request.form['forma_de_pagamento']
        status_pagamento = request.form['status_pagamento']
        movimentacao_tipo = request.form['movimentacao_tipo']
        movimentacao_categoria = request.form['movimentacao_categoria']
        valor = request.form['valor']
        observacao = request.form.get('observacao', '')

        print("2. Processando competencia...")
        # Extrair mes e ano da competencia (formato: "2025-08")
        ano, mes = competencia.split('-')
        mes = int(mes)
        ano = int(ano)
        print(f"mes/ano extraidos: {mes}/{ano}")

        print("3. Validando valor...")
        valor_float = float(valor)
        if valor_float < 0:
            raise ValueError('Valor nao pode ser negativo')

        print("4. Convertendo datas...")
        data_cadastro_obj = datetime.strptime(data_cadastro, '%Y-%m-%d').date()
        data_obj = datetime.strptime(data, '%Y-%m-%d').date()

        resultado = {
            'data_cadastro': data_cadastro_obj,
            'operacao': operacao,
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

        print("=== SUCESSO ===")
        print(f"Resultado: {resultado}")
        return resultado

    except Exception as e:
        print(f"=== ERRO: {e} ===")
        import traceback
        traceback.print_exc()
        raise e


@movimentacoes_bp.route('/nova_movimentacao', methods=['GET', 'POST'])
def nova_movimentacao():
    print("Entrou na rota")

    if request.method == 'POST':
        print("Method POST detectado")

        print("Dados recebidos:")
        for key, value in request.form.items():
            print(f"{key}: {value}")

        try:
            print("Iniciando processamento...")
            dados = processar_dados_form()
            print("Dados processados!")

            print(f"Tipo de dados: {type(dados)}")
            print(f"Dados: {dados}")

            if dados is None:
                print("ERRO: dados retornou None!")
                raise ValueError("Dados nao foram processados corretamente")
            print("Criando objeto Movimentacao...")
            print(f"data_cadastro: {dados.get('data_cadastro', 'NAO ENCONTRADO')}")
            print(f"operacao: {dados.get('operacao', 'NAO ENCONTRADO')}")

            nova_mov = Movimentacao(
                data_cadastro=dados['data_cadastro'],
                operacao=dados['operacao'],
                data=dados['data'],
                descricao=dados['descricao'],
                forma_de_pagamento=dados['forma_de_pagamento'],
                status_pagamento=dados['status_pagamento'],
                mes=dados['mes'],
                ano=dados['ano'],
                movimentacao_tipo=dados['movimentacao_tipo'],
                movimentacao_categoria=dados['movimentacao_categoria'],
                valor=dados['valor'],
                observacao=dados['observacao']
                )
            
            print("Objeto criado com sucesso!")
            print(f"Objeto: {nova_mov}")

            db.session.add(nova_mov)
            print("Adicionado na sessao")
            db.session.commit()
            print("Commit feito")

            flash('Sucesso!', 'success')
            # return redirect(url_for('movimentacoes.listar_movimentacoes'))
            return render_template('index.html')
            

        except Exception as e:
            print(f"ERRO COMPLETO: {e}")
            print(f"Tipo do erro: {type(e)}")
            import traceback
            print("Traceback completo:")
            traceback.print_exc()
            flash(f'Erro: {str(e)}', 'danger')
            db.session.rollback()

    return render_template('movimentacoes/movimentacao_cadastro.html')




@movimentacoes_bp.route('/listar_movimentacoes')
def listar_movimentacoes():
    try:
        movimentacoes = Movimentacao.query.order_by(asc(Movimentacao.data)).all()
        return render_template('movimentacoes/movimentacoes_lista.html', movimentacoes=movimentacoes)
    except Exception as e:
        flash(f'Erro ao carregar movimentacoes: {str(e)}', 'danger')
        return render_template('movimentacoes/movimentacoes_lista.html', movimentacoes=[])

@movimentacoes_bp.route('/editar_movimentacao/<int:id>', methods=['GET', 'POST'])
def editar_movimentacao(id):
    movimentacao = Movimentacao.query.get_or_404(id)

    if request.method == 'POST':
        try:
            dados = processar_dados_form()
            
            movimentacao.data_cadastro = dados['data_cadastro']
            movimentacao.operacao = dados['operacao']
            movimentacao.data = dados['data']
            movimentacao.descricao = dados['descricao']
            movimentacao.forma_de_pagamento = dados['forma_de_pagamento']
            movimentacao.status_pagamento = dados['status_pagamento']
            movimentacao.mes = dados['mes']
            movimentacao.ano = dados['ano']
            movimentacao.movimentacao_tipo = dados['movimentacao_tipo']
            movimentacao.movimentacao_categoria = dados['movimentacao_categoria']
            movimentacao.valor = dados['valor']
            movimentacao.observacao = dados['observacao']

            db.session.commit()
            flash('Movimentacao atualizada com sucesso!', 'success')
            return redirect(url_for('movimentacoes.listar_movimentacoes'))

        except ValueError as e:
            flash(f'Erro de validacao: {str(e)}', 'danger')
            db.session.rollback()
        except Exception as e:
            flash(f'Erro inesperado ao atualizar: {str(e)}', 'danger')
            db.session.rollback()
    
    return render_template('movimentacoes/movimentacao_cadastro.html', movimentacao=movimentacao)

@movimentacoes_bp.route('/deletar_movimentacao/<int:id>', methods=['POST'])
def deletar_movimentacao(id):
    try:
        movimentacao = Movimentacao.query.get_or_404(id)
        db.session.delete(movimentacao)
        db.session.commit()
        flash('Movimentacao deletada com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao deletar movimentacao: {str(e)}', 'danger')
        db.session.rollback()
    
    return redirect(url_for('movimentacoes.listar_movimentacoes'))
