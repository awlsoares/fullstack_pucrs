from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Flask
from models import db, Contrato, Cliente, Proposta, NotaFiscal
from datetime import date, datetime
import requests
from sqlalchemy import extract, asc, desc
from dateutil.relativedelta import relativedelta 

contratos_bp = Blueprint('contratos', __name__)
 
@contratos_bp.route('/novo_contrato', methods=['GET', 'POST'])
def novo_contrato():
    clientes = Cliente.query.order_by(asc(Cliente.nome)).all()

    if request.method == 'POST':
        data_assinatura = request.form['data_assinatura']

        ano_assinatura = datetime.strptime(data_assinatura, "%Y-%m-%d").date().year
        qtd_contratos_ano  = Contrato.query.filter(extract('year', Contrato.data_assinatura) == ano_assinatura).count()
        numero_contrato = f"{qtd_contratos_ano + 1}/{str(ano_assinatura)[-2:]}"

        cliente_id = request.form['cliente_id']
        escopo = request.form['escopo']        
        valor_assinatura = request.form['valor_assinatura']
        valor_protocolo = request.form['valor_protocolo']
        valor_conclusao = request.form['valor_conclusao']
        observacao = request.form['observacao']

        try:
            contrato = Contrato(
                numero_contrato=numero_contrato,
                data_assinatura=data_assinatura,
                cliente_id=cliente_id,
                escopo=escopo,
                valor_assinatura = float(valor_assinatura),
                valor_protocolo=float(valor_protocolo),
                valor_conclusao=float(valor_conclusao),
                observacao=observacao
            )
            db.session.add(contrato)
            db.session.commit()
            flash('Contrato cadastrado com sucesso!', 'success')
            return redirect(url_for('contratos.listar_contratos'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash('Erro inesperado ao salvar: ' + str(e), 'danger')

    return render_template('contratos/contratos_cadastro.html', clientes=clientes)


@contratos_bp.route('/contratos')
def listar_contratos():
    cliente_id = request.args.get('cliente_id')
    clientes = Cliente.query.all()

    propostas = Proposta.query.all()
    
    if cliente_id:
        # contratos = Contrato.query.filter_by(cliente_id=cliente_id).all()
        contratos = (Contrato.query.join(Proposta).filter(Contrato.cliente_id == cliente_id,Proposta.status_proposta == 'Aprovado').order_by(Contrato.data_assinatura).all())
    else:
        # contratos = Contrato.query.join(Proposta).filter(Proposta.status_proposta == 'Aprovado').order_by(Contrato.data_assinatura).all()
        contratos = Contrato.query.join(Proposta).filter(Proposta.status_proposta == 'Aprovado').order_by(desc(Contrato.data_assinatura)).all()
        

    return render_template(
        'contratos/contratos_lista.html', 
        contratos=contratos, 
        clientes=clientes, 
        cliente_id=cliente_id,
        propostas=propostas)


@contratos_bp.route('/contratos/faturamento/atualizar_status', methods=['POST'])
def atualizar_status_faturamento():
    print("Entrou em atualizar_status_faturamento.")
    data = request.get_json()
    if not data:
        return jsonify(success=False, message="Dados JSON não enviados"), 400
    
    hoje = date.today()
    contrato_id = data.get('contrato_id')
    tipo = data.get('tipo')
    data_faturamento = data.get('data_faturamento')
    statusAtualTexto = data.get('statusAtualTexto')
    print(f"Hoje: {hoje} - ID: {contrato_id} - Tipo: {tipo} - Data Faturamento: { data_faturamento}")
    
    if not contrato_id or tipo not in ['assinatura', 'protocolo', 'conclusao']:
        return jsonify(success=False, message="Parâmetros inválidos (contrato ou tipo.)"), 400 

    contrato = Contrato.query.get(contrato_id)
    if not contrato:
        return jsonify(success=False, message="Contrato não encontrado"), 404

    try:
        print("Entrou no try!")
        print("------- Status atual texto: ", statusAtualTexto, "---------")
        if statusAtualTexto == "Não Faturado":
            return jsonify({
                'success': True,
                'redirect': url_for('nfs.nova_nf', tipo=tipo, contrato_id=contrato_id, data_faturamento=data_faturamento)
            })
        else:         

            if tipo == 'assinatura':
                contrato.status_assinatura = False
                contrato.data_faturamento_assinatura = hoje
                db.session.commit()
                
                notas_fiscais = NotaFiscal.query.filter(
                    NotaFiscal.contrato_id == contrato_id,
                    NotaFiscal.tipo_servico == 'Assinatura'
                ).all()                

            elif tipo == 'protocolo':
                contrato.status_protocolo = False
                contrato.data_faturamento_protocolo = hoje
                db.session.commit()

                notas_fiscais = NotaFiscal.query.filter(
                    NotaFiscal.contrato_id == contrato_id,
                    NotaFiscal.tipo_servico == 'Protocolo'
                ).all()

            elif tipo == 'conclusao':
                contrato.status_conclusao = False
                contrato.data_faturamento_conclusao = hoje
                db.session.commit()

                notas_fiscais = NotaFiscal.query.filter(
                    NotaFiscal.contrato_id == contrato_id,
                    NotaFiscal.tipo_servico == 'Conclusão'
                ).all()
            
            # Excluir todas as notas fiscais encontradas
            print(notas_fiscais)
            for nota in notas_fiscais:
                # Construir a URL para a rota de exclusão
                delete_url = url_for('nfs.delete_nota_fiscal', id=nota.id, _external=True)
                # Fazer a chamada POST para a rota de exclusão
                response = requests.post(delete_url)

                if response.status_code != 200:
                    print(f"Erro ao excluir Nota Fiscal {nota.id}: {response.json()}")
            
            db.session.commit()
            

            return jsonify({
                'success': True,
                'redirect': url_for('contratos.listar_contratos')  # Ajustar aqui para 'nfs.listar_nfs'
            })


    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message=str(e)), 500


@contratos_bp.route('/contratos/atualizar_status_contrato', methods=['POST'])
def atualizar_status_contrato():
    data = request.get_json()
    if not data:
        return jsonify(success=False, message="Dados JSON não enviados"), 400
    
    contrato_id = data.get('contrato_id')
    status_contrato = data.get('status_contrato')

    contrato = Contrato.query.get(contrato_id)
    if not contrato:
        return jsonify(success=False, message="Contrato não encontrado"), 404

    try:
        contrato.status_contrato = status_contrato
        db.session.commit()
        return jsonify(success=True)

    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message=str(e)), 500


@contratos_bp.route('/contratos/<int:contrato_id>/editar', methods=['GET', 'POST'])
def editar_contrato(contrato_id):
    contrato = Contrato.query.get_or_404(contrato_id)
    proposta = contrato.proposta
    cliente = proposta.cliente
    # cliente_id = contrato.cliente_id
    # cliente = Cliente.query.get_or_404(cliente_id)
    # proposta = Proposta.query.filter_by(contrato_id=contrato_id).first()
    numero_proposta = proposta.numero_proposta


    if request.method == 'POST':

        #contrato.numero_contrato = request.form['numero_contrato']
        contrato.data_assinatura = request.form['data_assinatura']
        # contrato.cliente_id = request.form['cliente_id']
        contrato.cliente_id = cliente.id
        contrato.escopo = request.form['escopo']
        contrato.valor_assinatura = request.form['valor_assinatura']
        contrato.valor_protocolo = request.form['valor_protocolo']
        contrato.valor_conclusao = request.form['valor_conclusao']
        

        try:
            db.session.commit() 
            flash('Contrato atualizado com sucesso!', 'success')
            return redirect(url_for('contratos.listar_contratos'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao atualizar contrato: ' + str(e), 'danger')
    return render_template(
                'contratos/contratos_cadastro.html', 
                cliente=cliente,
                escopo=contrato.escopo,
                valor_assinatura=contrato.valor_assinatura,
                valor_protocolo=contrato.valor_protocolo,
                valor_conclusao=contrato.valor_conclusao, 
                observacao=contrato.observacao,
                numero_contrato=contrato.numero_contrato,
                numero_proposta=numero_proposta,
                contrato=contrato)

# Geração do contrato proveniente de uma proposta aprovada
@contratos_bp.route('/novo_contrato/proposta_aprovada/<int:proposta_id>', methods=['GET', 'POST'])
def novo_contrato_proposta_aprovada(proposta_id):
    print("-----------------------Entrou em novo_contrato_proposta_aprovada")
    proposta = Proposta.query.get_or_404(proposta_id)
    print(proposta)
    cliente_id = proposta.cliente_id
    cliente = Cliente.query.get_or_404(cliente_id)
    escopo = proposta.escopo
    valor_assinatura = proposta.valor_assinatura
    valor_protocolo = proposta.valor_protocolo
    valor_conclusao = proposta.valor_conclusao
    observacao = proposta.observacao
    numero_proposta = proposta.numero_proposta
    data = date.today()

    if request.method == 'POST':
        data_assinatura = request.form['data_assinatura']
        ano_assinatura = datetime.strptime(data_assinatura, "%Y-%m-%d").date().year
        qtd_contratos_ano  = Contrato.query.filter(extract('year', Contrato.data_assinatura) == ano_assinatura).count()
        numero_contrato = f"{qtd_contratos_ano + 1}/{str(ano_assinatura)[-2:]}"

        observacao = request.form['observacao']

        try:
            contrato = Contrato(
                numero_contrato=numero_contrato,
                data_assinatura=data_assinatura,
                # data_assinatura = proposta.data_envio,
                cliente_id=cliente_id, 
                escopo=escopo,
                valor_assinatura = valor_assinatura,
                valor_protocolo=valor_protocolo,
                valor_conclusao=valor_conclusao,
                observacao=observacao,
                proposta_id=proposta_id
            )
            db.session.add(contrato)
            db.session.commit()

            proposta = Proposta.query.get_or_404(proposta_id)
            proposta.contrato_id = contrato.id   #Tentativa de atualizar o contrato_id na tabela Proposta.
            db.session.commit()
            

            flash('Contrato cadastrado com sucesso!', 'success')
            return redirect(url_for('contratos.listar_contratos'))
            # return redirect(url_for('propostas.listar_propostas'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash('Erro inesperado ao salvar: ' + str(e), 'danger')

    return render_template('contratos/contratos_cadastro_pela_proposta_aprovada.html', 
                        cliente=cliente,
                        escopo=escopo,
                        valor_assinatura=valor_assinatura,
                        valor_protocolo=valor_protocolo,
                        valor_conclusao=valor_conclusao,
                        observacao=observacao,
                        numero_proposta=numero_proposta,
                        data=data
                        )

# Duplicação de contrato múltiplos
@contratos_bp.route('/duplicar_contrato/<int:proposta_id>', methods=['POST'])
def duplicar_contrato(proposta_id):
    # Pega o contrato mais recente da proposta
    contrato_base = (Contrato.query
                     .filter_by(proposta_id=proposta_id)
                     .order_by(Contrato.data_assinatura.desc())
                     .first())
    
    if not contrato_base:
        flash("Não há contratos anteriores para duplicar.", "warning")
        return redirect(url_for('contratos.listar_contratos'))

    try:
        # Incrementa 1 mês na data de assinatura
        nova_data = contrato_base.data_assinatura + relativedelta(months=1)

        # Calcula número do contrato no ano da nova data
        ano_assinatura = nova_data.year
        qtd_contratos_ano = Contrato.query.filter(
            extract('year', Contrato.data_assinatura) == ano_assinatura
        ).count()
        numero_contrato = f"{qtd_contratos_ano + 1}/{str(ano_assinatura)[-2:]}"

        # Cria novo contrato
        novo_contrato = Contrato(
            numero_contrato=numero_contrato,
            data_assinatura=nova_data,
            cliente_id=contrato_base.cliente_id,
            escopo=contrato_base.escopo,
            valor_assinatura=contrato_base.valor_assinatura,
            valor_protocolo=contrato_base.valor_protocolo,
            valor_conclusao=contrato_base.valor_conclusao,
            observacao=contrato_base.observacao,
            proposta_id=proposta_id
        )
        db.session.add(novo_contrato)
        db.session.commit()

        flash("Contrato duplicado com sucesso!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao duplicar contrato: {str(e)}", "danger")

    return redirect(url_for('contratos.listar_contratos'))

@contratos_bp.route('/deletar_contrato/<int:id>', methods=['POST'])
def deletar_contrato(id):
    try:
        contrato = Contrato.query.get_or_404(id)
        if contrato.status_assinatura == False and contrato.status_protocolo == False and contrato.status_conclusao == False:
            db.session.delete(contrato)
            db.session.commit()
            flash('Contrato deletado com sucesso!', 'success')
        else:
            flash('Não é possível deletar um contrato com uma nota fiscal faturada!', 'error')
    except Exception as e:
        flash(f'Erro ao deletar contrato: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('contratos.listar_contratos'))
