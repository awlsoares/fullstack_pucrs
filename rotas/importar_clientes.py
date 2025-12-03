from flask import Blueprint, redirect, url_for, flash
from importar.clientes_importar import importar_clientes

importar_clientes_bp = Blueprint('importar_clientes', __name__)

@importar_clientes_bp.route('/importar_clientes')
def importar_dados():
    caminho_excel = r"C:\Users\EG2A\OneDrive - PETROBRAS\Desktop\sistema_essencial_v1-main\dados.xlsx"
    try:
        importar_clientes(caminho_excel)
        flash('Importação da lista de Clientes concluída com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro na importação: {str(e)}', 'danger')
    # Redireciona para a página inicial ou listagem de movimentações
    return redirect(url_for('clientes.listar_clientes'))
