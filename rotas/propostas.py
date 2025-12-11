from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, Cliente, Proposta, Contrato, NotaFiscal, Movimentacao
from datetime import date, datetime
from sqlalchemy import extract, asc
 
propostas_bp = Blueprint('propostas', __name__)

def br_to_float(valor_str: str) -> float:
    if not valor_str:
        return 0.0
    return float(valor_str.replace('.', '').replace(',', '.'))

 
@propostas_bp.route('/nova_proposta', methods=['GET', 'POST'])
def nova_proposta():
    # clientes = Cliente.query.all()  # Para preencher o select no formulário
    clientes = Cliente.query.order_by(asc(Cliente.nome)).all() # Para preencher o select no formulário

    # if len(clientes) == 0:
    #     return render_template('clientes/clientes_cadastro.html')
    
    msg_assinatura = False
    msg_protocolo = False
    msg_conclusao = False

    if request.method == 'POST':
        data_envio = request.form['data_envio']

        ano_envio = datetime.strptime(data_envio, "%Y-%m-%d").date().year
        qtd_propostas_ano  = Proposta.query.filter(extract('year', Proposta.data_envio) == ano_envio).count()
        #print(f"Ano: {ano_envio} Quantidade: { qtd_propostas_ano}.")
        numero_proposta = f"{qtd_propostas_ano + 1}/{str(ano_envio)[-2:]}"

        cliente_id = request.form['cliente_id']
        escopo = request.form['escopo']

        contratos_multiplos = request.form.get('contratos_multiplos')
        if contratos_multiplos == "on":
            contratos_multiplos = True
        else:
            contratos_multiplos = False

        valor_assinatura = br_to_float(request.form['valor_assinatura'])
        valor_protocolo = br_to_float(request.form['valor_protocolo'])
        valor_conclusao = br_to_float(request.form['valor_conclusao'])
        observacao = request.form['observacao']
        
        try:
            proposta = Proposta(
                numero_proposta=numero_proposta,
                data_envio=data_envio,
                cliente_id=cliente_id,
                contratos_multiplos = contratos_multiplos,
                escopo=escopo,
                valor_assinatura = valor_assinatura,
                valor_protocolo = valor_protocolo,
                valor_conclusao = valor_conclusao,

                observacao = observacao
            )

            db.session.add(proposta)
            db.session.commit()

            flash('Proposta cadastrada com sucesso!', 'success')
            return redirect(url_for('propostas.listar_propostas'))
        
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash('Erro inesperado ao salvar: ' + str(e), 'danger')

    return render_template(
        'propostas/proposta_cadastro.html',
        clientes=clientes,
        msg_assinatura = msg_assinatura,
        msg_protocolo = msg_protocolo,
        msg_conclusao = msg_conclusao
        )

@propostas_bp.route('/propostas')
def listar_propostas():
    cliente_id = request.args.get('cliente_id')
    status_nome = request.args.get('status_nome')

    clientes = Cliente.query.order_by(asc(Cliente.nome)).all()
    contratos = Contrato.query.all()

    # Monta query base
    query = Proposta.query

    if cliente_id:
        query = query.filter(Proposta.cliente_id == cliente_id)

    if status_nome:
        query = query.filter(Proposta.status_proposta == status_nome)

    # Executa a query ordenando
    propostas = query.order_by(Proposta.data_envio).all()

    return render_template(
        'propostas/propostas_lista.html',
        propostas=propostas,
        clientes=clientes,
        cliente_id=cliente_id,
        contratos=contratos,
        status_nome=status_nome
    )

@propostas_bp.route('/propostas/atualizar_status_proposta', methods=['POST'])
def atualizar_status_proposta():
    data = request.get_json()
    if not data:
        return jsonify(success=False, message="Dados JSON não enviados"), 400
    
    proposta_id = data.get('proposta_id') 
    status_proposta = data.get('status_proposta')

    proposta = Proposta.query.get(proposta_id)
    if not proposta:
        return jsonify(success=False, message="Proposta não encontrada"), 404

    try:
        # Atualiza o status
        proposta.status_proposta = status_proposta

        # Se o status for Revisado, cria uma nova versão
        if status_proposta == 'Revisado':
            # Aqui você precisa receber os novos valores que serão atualizados
            # (ou buscar de outra rota, depende da sua lógica)
            nova_data_envio = datetime.today().date()  # ou algo que venha do JSON
            nova_assinatura = float(data.get('valor_assinatura', proposta.valor_assinatura))
            novo_protocolo = float(data.get('valor_protocolo', proposta.valor_protocolo))
            novo_conclusao = float(data.get('valor_conclusao', proposta.valor_conclusao))

            # Chama o método do model que salva histórico e atualiza os valores
            proposta.criar_nova_versao(
                nova_assinatura=nova_assinatura,
                novo_protocolo=novo_protocolo,
                novo_conclusao=novo_conclusao,
                nova_data_envio=nova_data_envio
            )

            # Depois de criar nova versão, você pode alterar o status de volta ou manter Revisado
            # proposta.status_proposta = 'Em revisão'  # exemplo se quiser voltar status

        db.session.commit()
        return jsonify(success=True)

    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message=str(e)), 500

@propostas_bp.route('/propostas/<int:proposta_id>/editar', methods=['GET', 'POST'])
def editar_proposta(proposta_id):
    print(f"Entrou em editar_proposta({proposta_id}).")
    proposta = Proposta.query.get_or_404(proposta_id)
    msg_assinatura = False
    msg_protocolo = False
    msg_conclusao = False

    # if proposta.contrato_id != None:
    #     contrato = Contrato.query.get_or_404(proposta.contrato_id)
    #     if contrato.status_assinatura == True:
    #         msg_assinatura = True
    #     if contrato.status_protocolo == True:
    #         msg_protocolo = True
    #     if contrato.status_aprovacao == True:
    #         msg_conclusao = True

    cliente_da_proposta = proposta.cliente_id
    clientes = Cliente.query.order_by(asc(Cliente.nome)).all()
    if request.method == 'POST':

        #proposta.numero_proposta = request.form['numero_proposta']

        # Atualiza o numero_proposta no formato id_ano
        # proposta.numero_proposta = f"{proposta.id}_{data_envio.year}"

        proposta.data_envio = request.form['data_envio']
        proposta.cliente_id = request.form['cliente_id']
        proposta.escopo = request.form['escopo']
        contratos_multiplos = request.form.get('contratos_multiplos')
        if contratos_multiplos == "on":
            proposta.contratos_multiplos = True
        else:
            proposta.contratos_multiplos = False

        proposta.valor_assinatura = br_to_float(request.form['valor_assinatura'])
        proposta.valor_protocolo = br_to_float(request.form['valor_protocolo'])
        proposta.valor_conclusao = br_to_float(request.form['valor_conclusao'])

        proposta.observacao = request.form['observacao']

        try:
            print(f"Entrou no 'try'")
            db.session.commit()
            flash('Proposta atualizada com sucesso!', 'success')

            # if proposta.contrato_id != None:

            #     contrato = Contrato.query.get_or_404(proposta.contrato_id)
            #     contrato.cliente_id = proposta.cliente_id
            #     contrato.escopo = proposta.escopo
            #     contrato.valor_assinatura = proposta.valor_assinatura
            #     contrato.valor_protocolo = proposta.valor_protocolo
            #     contrato.valor_conclusao = proposta.valor_conclusao
            #     contrato.observacao = proposta.observacao

            #     db.session.commit()

            #     # contrato = Contrato.query.get_or_404(proposta.contrato_id)
            #     contrato_id = proposta.contrato_id
            #     if contrato.status_assinatura == True:
            #         print("-------- Entrou em contrato.status_assinatura")
            #         nota_fiscal = NotaFiscal.query.filter(
            #                 NotaFiscal.contrato_id == contrato_id,
            #                 NotaFiscal.tipo_servico == 'Assinatura'
            #             ).first()
            #         nota_fiscal.valor_bruto = contrato.valor_assinatura
            #         db.session.commit()

            #     if contrato.status_protocolo == True:
            #         print("-------- Entrou em contrato.status_protocolo")
            #         nota_fiscal = NotaFiscal.query.filter(
            #                 NotaFiscal.contrato_id == contrato_id,
            #                 NotaFiscal.tipo_servico == 'Protocolo'
            #             ).first()
            #         nota_fiscal.valor_bruto = contrato.valor_protocolo
            #         db.session.commit()

            #     if contrato.status_aprovacao == True:
            #         print("-------- Entrou em contrato.status_aprovacao")
            #         nota_fiscal = NotaFiscal.query.filter(
            #                 NotaFiscal.contrato_id == contrato_id,
            #                 NotaFiscal.tipo_servico == 'Conclusão'
            #             ).first()
            #         nota_fiscal.valor_bruto = contrato.valor_aprovacao
            #         db.session.commit()

            return redirect(url_for('propostas.listar_propostas'))
        
        except Exception as e:
            db.session.rollback()
            flash('Erro ao atualizar projeto: ' + str(e), 'danger')

    print("Mensagem Assinatura: ", msg_assinatura)
    return render_template(
        'propostas/proposta_cadastro.html', 
        proposta=proposta, 
        clientes=clientes,
        cliente_da_proposta=cliente_da_proposta,
        msg_assinatura = msg_assinatura,
        msg_protocolo = msg_protocolo,
        msg_conclusao = msg_conclusao)

@propostas_bp.route('/nova_versao_proposta/<int:id>', methods=['GET', 'POST'])
def nova_versao_proposta(id):
    print(f"Entrou em nova_versao_proposta({id}).")
    proposta = Proposta.query.get_or_404(id)

    nova_assinatura = br_to_float(request.form['valor_assinatura'])
    novo_protocolo = br_to_float(request.form['valor_protocolo'])
    novo_conclusao = br_to_float(request.form['valor_conclusao'])

    nova_data_envio = request.form['data_envio']
    novo_cliente_id = request.form['cliente_id']
    novo_escopo = request.form['escopo']
    contratos_multiplos = request.form.get('contratos_multiplos') == "on"
    nova_observacao = request.form['observacao']

    try:
        proposta.criar_nova_versao(
            nova_assinatura=nova_assinatura,
            novo_protocolo=novo_protocolo,
            novo_conclusao=novo_conclusao,
            nova_data_envio=datetime.strptime(nova_data_envio, "%Y-%m-%d").date()
        )

        proposta.cliente_id = int(novo_cliente_id)
        proposta.escopo = novo_escopo
        proposta.contratos_multiplos = contratos_multiplos
        proposta.observacao = nova_observacao

        db.session.commit()
        flash('Nova Versão da Proposta criada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao criar nova versão da Proposta: {str(e)}', 'danger')

    return redirect(url_for('propostas.listar_propostas'))

@propostas_bp.route('/cancelar_proposta/<int:id>', methods=['POST'])
def cancelar_proposta(id):
    try:
        proposta = Proposta.query.get_or_404(id)
        proposta.status_proposta = 'Cancelada'
        db.session.commit()
        flash('Proposta cancelada com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao cancelar Proposta: {str(e)}', 'danger')
        db.session.rollback()
    
    return redirect(url_for('propostas.listar_propostas'))