class MovimentacaoTipo(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(db.String(100), nullable=False)
    observacao = db.Column(db.String(300), nullable=False)

    def __repr__(self):
        return f"<Tipo de Movimentação: {self.nome}>"
    
class MovimentacaoCategoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(db.String(100), nullable=False)
    observacao = db.Column(db.String(300), nullable=False)

    def __repr__(self):
        return f"<Tipo de Categoria: {self.nome}>"