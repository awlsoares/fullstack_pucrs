from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, Cliente, Banco, NotaFiscal, Contrato
from datetime import date 


from sqlalchemy import extract, func
from collections import defaultdict

nfs_bp_index = Blueprint('nfs_index', __name__)

def gerar_dicionario_notas_por_ano():
    # Consulta para agrupar por ano e contar as notas fiscais
    resultados = db.session.query(
        extract('year', NotaFiscal.data_emissao).label('ano'),
        func.count(NotaFiscal.id).label('quantidade')
    ).group_by(
        extract('year', NotaFiscal.data_emissao)
    ).all()

    # Converte os resultados em um dicionário
    dicionario_notas = {int(ano): quantidade for ano, quantidade in resultados}

    return dicionario_notas

@nfs_bp_index.route('/api/notas_por_ano', methods=['GET'])
def notas_por_ano():
    dicionario_notas = gerar_dicionario_notas_por_ano()
    return jsonify(dicionario_notas)

@nfs_bp_index.route('/api/notas_por_mes_ano', methods=['GET'])
def notas_por_mes_ano():
    ano = request.args.get('ano', type=int)
    mes = request.args.get('mes', type=int)
    
    query = db.session.query(
        extract('year', NotaFiscal.data_emissao).label('ano'),
        extract('month', NotaFiscal.data_emissao).label('mes'),
        func.count(NotaFiscal.id).label('quantidade')
    ).group_by(
        extract('year', NotaFiscal.data_emissao),
        extract('month', NotaFiscal.data_emissao)
    )
    
    if ano:
        query = query.filter(extract('year', NotaFiscal.data_emissao) == ano)
    if mes:
        query = query.filter(extract('month', NotaFiscal.data_emissao) == mes)

    resultados = query.all()
    dados_filtrados = [{'ano': int(ano), 'mes': int(mes), 'quantidade': quantidade} for ano, mes, quantidade in resultados]
    return jsonify(dados_filtrados)

@nfs_bp_index.route('/api/anos_disponiveis', methods=['GET'])
def anos_disponiveis():
    # Consulta para obter todos os anos únicos de emissão das notas fiscais
    anos = db.session.query(
        func.distinct(extract('year', NotaFiscal.data_emissao))
    ).order_by(extract('year', NotaFiscal.data_emissao)).all()

    anos_disponiveis = [int(ano[0]) for ano in anos]  # Converte para lista de inteiros
    print(anos_disponiveis)
    return jsonify(anos_disponiveis)
