from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask import Flask, flash
from sqlalchemy import asc
from models import db, Banco

bancos_bp = Blueprint('bancos', __name__)

@bancos_bp.route('/novo_banco', methods=['GET', 'POST'])
def novo_banco():

    if request.method == 'POST':
        nome = request.form['nome']
        numero_conta = request.form['numero_conta']
        observacao = request.form['observacao'] 
        
        try:
            novo = Banco(nome=nome, observacao=observacao, numero_conta=numero_conta)
            db.session.add(novo)
            db.session.commit()
            flash('Banco cadastrado com sucesso!', 'success')
            return redirect(url_for('bancos.listar_bancos'))
        except ValueError as e:
            flash(str(e), 'danger')  # Mostra erro de validação (ex: idade inválida)
        except Exception as e:
            flash('Erro inesperado ao salvar: ' + str(e), 'danger')
    return render_template('bancos/bancos_cadastro.html')

@bancos_bp.route('/bancos')
def listar_bancos():
    bancos = Banco.query.order_by(asc(Banco.nome)).all()
    return render_template('bancos/bancos_lista.html', bancos=bancos)

@bancos_bp.route('/bancos/<int:banco_id>/editar', methods=['GET', 'POST'])
def editar_banco(banco_id):
    banco = Banco.query.get_or_404(banco_id)
    if request.method == 'POST':
        banco.nome = request.form['nome']
        banco.numero_conta = request.form['numero_conta']
        banco.observacao = request.form['observacao']

        try:
            db.session.commit()
            flash('Banco atualizado com sucesso!', 'success')
            return redirect(url_for('bancos.listar_bancos'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao atualizar banco: ' + str(e), 'danger')
    return render_template('bancos/bancos_cadastro.html', banco=banco)