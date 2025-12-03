from flask.cli import FlaskGroup
from app import app, db  # Ajuste se o nome do seu arquivo principal for diferente de `app.py`
from flask_migrate import Migrate

# IMPORTAR MODELS PARA ALEMBIC DETECTAR
from app import models  # <-- isso garante que todos os modelos sejam carregados

migrate = Migrate(app, db)
cli = FlaskGroup(app)

if __name__ == "__main__":
    cli()

