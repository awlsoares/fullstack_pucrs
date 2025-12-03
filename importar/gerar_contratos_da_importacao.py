from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Flask
from models import db, Contrato, Cliente, Proposta, NotaFiscal
from datetime import date, datetime
import requests
from sqlalchemy import extract
from dateutil.relativedelta import relativedelta 
 

gerar_contratos_da_importacao_bp = Blueprint('gerar_contratos_da_importacao', __name__)

@gerar_contratos_da_importacao_bp.route('/gerar_contratos_da_importacao')
def gerar_contratos_da_importacao():
    propostas = Proposta.query.all()
    contador = 1
    for proposta in propostas:
        if proposta.status_proposta == "Aprovado":
            print(f"------ Entrou no loop: {contador}.")
            proposta_id = proposta.id
            cliente_id = proposta.cliente_id
            # cliente = Cliente.query.get_or_404(cliente_id) 
            escopo = proposta.escopo
            valor_assinatura = proposta.valor_assinatura
            valor_protocolo = proposta.valor_protocolo
            valor_conclusao = proposta.valor_conclusao
            observacao = proposta.observacao
            numero_proposta = proposta.numero_proposta
            data = date.today()

            data_assinatura = proposta.data_envio

            ano_assinatura = data_assinatura.year
            qtd_contratos_ano  = Contrato.query.filter(extract('year', Contrato.data_assinatura) == ano_assinatura).count()
            numero_contrato = f"{qtd_contratos_ano + 1}/{str(ano_assinatura)[-2:]}"

            try:
                print("Entrou no try.")
                contrato = Contrato(
                    numero_contrato=numero_contrato,
                    data_assinatura=data_assinatura,
                    cliente_id=cliente_id, 
                    escopo=escopo,
                    valor_assinatura = valor_assinatura,
                    valor_protocolo=valor_protocolo,
                    valor_conclusao=valor_conclusao,
                    observacao=observacao,
                    proposta_id=proposta_id
                )
                db.session.add(contrato)
                # db.session.commit()

                proposta = Proposta.query.get_or_404(proposta_id)
                proposta.contrato_id = contrato.id   #Tentativa de atualizar o contrato_id na tabela Proposta.
                # db.session.commit()

            except Exception as e:
                db.session.rollback()
                print(f"Erro ao criar o Contrato {numero_contrato} da Proposta {numero_proposta}: {e}")
            contador = contador + 1
                               
    # Commit geral no final
    try:
        db.session.commit()
        print("Todas os contratos foram criados com sucesso.")
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao salvar contratos: {e}")
    
    return redirect(url_for('contratos.listar_contratos'))