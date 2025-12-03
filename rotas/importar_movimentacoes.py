# rotas/importar_movimentacoes_bp.py
from flask import Blueprint, redirect, url_for, flash
from importar.movimentacoes_importar import importar_movimentacoes

importar_movimentacoes_bp = Blueprint('importar_movimentacoes', __name__)

@importar_movimentacoes_bp.route('/importar_movimentacoes')
def importar_dados():
    caminho_excel = r"C:\Users\EG2A\OneDrive - PETROBRAS\Desktop\sistema_essencial_v1-main\dados.xlsx"
    try:
        importar_movimentacoes(caminho_excel)
        flash('Importação da lista de Movimentações concluída com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro na importação: {str(e)}', 'danger')
    # Redireciona para a página inicial ou listagem de movimentações
    return redirect(url_for('movimentacoes.listar_movimentacoes'))
