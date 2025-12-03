from flask import Flask, render_template
from flask_migrate import Migrate
from models import db
from rotas.contratos import contratos_bp
from rotas.clientes import clientes_bp
from rotas.dashboard_faturamento import dashboard_faturamento_bp
from rotas.dashboard_recebimento import dashboard_recebimento_bp
from rotas.propostas import propostas_bp
from rotas.bancos import bancos_bp
from rotas.nfs import nfs_bp
from rotas.index import nfs_bp_index
from rotas.indicadores import indicadores_bp
from rotas.movimentacoes import movimentacoes_bp
from rotas.dados_rfb_dre import dados_rfb_dre_bp
from rotas.ajuda import ajuda_bp
from rotas.importar_movimentacoes import importar_movimentacoes_bp
from rotas.importar_propostas import importar_propostas_bp
from rotas.importar_clientes import importar_clientes_bp
from importar.gerar_contratos_da_importacao import gerar_contratos_da_importacao_bp

app = Flask(__name__)
app.secret_key = 'chave_super_secreta'  # Necessário para usar flash e sessões

# Configuração para conectar o sistema ao banco de dados PostgreSQL.
# dialeto://usuario:senha@host:porta/nome_do_banco

# MacBook
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://essencial_v2:essencial_v2@localhost:5432/essencial_v2'

# Notebook Windows
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://essencial_v1:essencial_v1@localhost:5432/essencial_v1'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://essencial_v3_win:essencial_v3_win@localhost:5432/essencial_v3_win'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# Registrar Blueprints
app.register_blueprint(contratos_bp)
app.register_blueprint(clientes_bp)
app.register_blueprint(dashboard_faturamento_bp)
app.register_blueprint(dashboard_recebimento_bp)
app.register_blueprint(propostas_bp)
app.register_blueprint(bancos_bp)
app.register_blueprint(nfs_bp)
app.register_blueprint(nfs_bp_index)
app.register_blueprint(indicadores_bp)
app.register_blueprint(movimentacoes_bp)
app.register_blueprint(dados_rfb_dre_bp)
app.register_blueprint(ajuda_bp)
app.register_blueprint(importar_movimentacoes_bp)
app.register_blueprint(importar_propostas_bp)
app.register_blueprint(importar_clientes_bp)
app.register_blueprint(gerar_contratos_da_importacao_bp)



@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)