from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import asc
from models import db, Cliente

clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route('/novo_cliente', methods=['GET', 'POST'])
def novo_cliente():

    if request.method == 'POST':
        nome = request.form['nome']
        observacao = request.form['observacao']
        cnpj = request.form['cnpj']
        
        try:
            novo = Cliente(nome=nome, observacao=observacao, cnpj=cnpj)
            db.session.add(novo)
            db.session.commit()
            #flash('Cliente cadastrado com sucesso!', 'success')
            return redirect(url_for('clientes.listar_clientes'))
        except ValueError as e:
            flash(str(e), 'danger')  # Mostra erro de validação (ex: idade inválida)
        except Exception as e:
            flash('Erro inesperado ao salvar: ' + str(e), 'danger')
    return render_template('clientes/clientes_cadastro.html')


@clientes_bp.route('/clientes')
def listar_clientes():
    clientes = Cliente.query.order_by(asc(Cliente.nome)).all()
    for cliente in clientes:
        print(cliente)
    return render_template('clientes/clientes_lista.html', clientes=clientes)

@clientes_bp.route('/clientes/<int:cliente_id>/editar', methods=['GET', 'POST'])
def editar_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    if request.method == 'POST':
        cliente.nome = request.form['nome']
        cliente.observacao = request.form['observacao']
        cliente.cnpj = request.form['cnpj']
        try:
            db.session.commit()
            flash('Cliente atualizado com sucesso!', 'success')
            return redirect(url_for('clientes.listar_clientes'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao atualizar cliente: ' + str(e), 'danger')
    return render_template('clientes/clientes_cadastro.html', cliente=cliente)
