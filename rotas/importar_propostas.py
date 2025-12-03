# rotas/importar_propostas_bp.py
from flask import Blueprint, redirect, url_for, flash
from importar.propostas_importar import importar_propostas

importar_propostas_bp = Blueprint('importar_propostas', __name__)

@importar_propostas_bp.route('/importar_propostas')
def importar_dados():
    caminho_excel = r"C:\Users\EG2A\OneDrive - PETROBRAS\Desktop\sistema_essencial_v1-main\dados.xlsx"
    try:
        importar_propostas(caminho_excel)
        flash('Importação da lista de Propostas concluída com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro na importação: {str(e)}', 'danger')
    # Redireciona para a página inicial ou listagem de movimentações
    return redirect(url_for('propostas.listar_propostas'))
