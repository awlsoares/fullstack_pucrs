from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, Cliente, Banco, NotaFiscal, Contrato, Movimentacao
from datetime import date, datetime
import traceback
from sqlalchemy import asc, desc
 
nfs_bp = Blueprint('nfs', __name__)
 
@nfs_bp.route('/nova_nf/<tipo>/<int:contrato_id>/<data_faturamento>', methods=['GET', 'POST'])
def nova_nf(tipo, contrato_id, data_faturamento):
    contrato = Contrato.query.get_or_404(contrato_id)
    data_faturamento = data_faturamento

    tipo = tipo    

    if tipo == 'Assinatura':
        valor_bruto = contrato.valor_assinatura
    elif tipo == 'Protocolo':
        valor_bruto = contrato.valor_protocolo
    else:
        valor_bruto = contrato.valor_conclusao

    cliente = contrato.cliente
    contrato_id = contrato.id
    bancos = Banco.query.all()

    if len(bancos) == 0:
        print("Sem banco cadastrado!")
        # return render_template('bancos/bancos_cadastro.html')

    forma_de_pagamento_opcoes = ['Boleto', 'Pix', 'TED', 'Outros']

    if request.method == 'POST':
        print("---------Entrou em POST -------------------")
        numero_nf = request.form['numero_nf']
        data_emissao = datetime.strptime(request.form['data_emissao'], '%Y-%m-%d').date()
        cliente_id = cliente.id
        valor_bruto = request.form['valor_bruto']
        valor_liquido = request.form['valor_liquido']
        forma_de_pagamento = request.form['forma_de_pagamento']
        boleto = request.form['boleto'].strip() or None
        banco_id = request.form['banco_id']
        data_vencimento = datetime.strptime(request.form['data_vencimento'], '%Y-%m-%d').date()
        contrato_id = contrato.id
        observacao = request.form['observacao']

        try:
            print("------ Entrou em try -----------------")

            cliente = Cliente.query.get(cliente_id)
            if not cliente:
                raise ValueError("Cliente não encontrado.")

            banco = Banco.query.get(banco_id)
            if not banco:
                raise ValueError("Banco não encontrado.")

            contrato = Contrato.query.get(contrato_id)
            if not contrato:
                raise ValueError("Contrato não encontrado.")
            

            if tipo == 'assinatura' or tipo == 'protocolo':
                tipo_servico = tipo.capitalize()
            else:
                tipo_servico = 'Conclusão'
            
            print(f"Dados recebidos para NF: numero_nf={numero_nf}, data_emissao={data_emissao}, cliente_id={cliente_id}, valor_bruto={valor_bruto}, valor_liquido={valor_liquido}, forma_de_pagamento={forma_de_pagamento}, boleto={boleto}, banco_id={banco_id}, data_vencimento={data_vencimento}, contrato_id={contrato_id}, observacao={observacao}, tipo_servico={tipo_servico}")
            #print(f"Dados recebidos para NF: numero_nf={type(numero_nf)}, data_emissao={type(data_emissao)}, cliente_id={type(cliente_id)}, valor_bruto={type(valor_bruto)}, valor_liquido={type(valor_liquido)}, forma_de_pagamento={type(forma_de_pagamento)}, boleto={type(boleto)}, banco_id={type(banco_id)}, data_vencimento={type(data_vencimento)}, contrato_id={type(contrato_id)}, observacao={type(observacao)}, tipo_servico={type(tipo_servico)}")


            nf = NotaFiscal(
                numero_nf=int(numero_nf),
                data_emissao=data_emissao,
                cliente_id=cliente_id,
                valor_bruto = float(valor_bruto),
                valor_liquido=float(valor_liquido),
                forma_de_pagamento=forma_de_pagamento,
                boleto = boleto,
                banco_id=int(banco_id),
                data_vencimento=data_vencimento,
                status_pagamento='No Prazo',
                contrato_id=int(contrato_id),
                observacao=observacao,
                tipo_servico=tipo_servico
            )
            db.session.add(nf)
            print(nf)

            if tipo == 'assinatura':
                contrato.status_assinatura = True
                contrato.data_faturamento_assinatura = data_faturamento

            elif tipo == 'protocolo':
                contrato.status_protocolo = True
                contrato.data_faturamento_protocolo = data_faturamento

            elif tipo == 'conclusao':
                contrato.status_conclusao = True
                contrato.data_faturamento_conclusao = data_faturamento

            db.session.flush()  # Valida os dados diretamente no banco
            db.session.commit()
            flash('Nota Fiscal cadastrada com sucesso!', 'success')

            # Cria uma movimentação com os dados da NF Criada #######################
            print(f"--------------Data de emissao {data_emissao}, mês: { data_emissao.month} e ano: { data_emissao.year}.")
            nova_movimentacao = Movimentacao(
                operacao = 'Entrada',
                data = data_vencimento,
                descricao = 'NF_' + numero_nf + '_Cliente_' + cliente.nome + '_Contrato_' + contrato.numero_contrato,
                forma_de_pagamento = forma_de_pagamento,  # "Boleto", "Pix", "TED", "Outros"
                status_pagamento = 'Aberto',  # 'Recebido', 'Pago', 'Aberto', 'Cancelado'
                mes = data_emissao.month,  # 1-12
                ano = data_emissao.year,  # 2024, 2025, etc. 
                
                movimentacao_tipo = 'Receita',
                movimentacao_categoria = 'Prestação de Serviço',
                
                valor = float(valor_liquido),
                observacao = 'Tipo de Serviço: ' + tipo_servico + ' - ' + observacao
            )
            
            db.session.add(nova_movimentacao)
            db.session.flush()  # Valida os dados diretamente no banco
            db.session.commit()



            # Renderiza diretamente o template da lista de Notas Fiscais
            today = date.today()
            cliente_id = cliente.id
            nfs = NotaFiscal.query.order_by(NotaFiscal.data_emissao).all()
            # return render_template('nfs/nfs_lista.html', nfs=nfs, clientes=[cliente], cliente_id=cliente_id, today=today)
        
            #Redireciona para a rota listar_nfs após criar a nota fiscal
            return redirect(url_for('nfs.listar_nfs'))
        
            # # Redireciona para a rota listar_contratos após criar a nota fiscal
            # return redirect(url_for('contratos.listar_contratos'))
            
        except ValueError as e:
            db.session.rollback()
            flash(str(e), 'danger')

        except Exception as e:
            db.session.rollback()
            flash('Erro inesperado ao salvar: ' + str(e), 'danger')
            print(traceback.format_exc())  # Exibe o traceback completo no console
            flash('Erro ao salvar Nota Fiscal: ' + str(e), 'danger')

    return render_template('nfs/nf_cadastro.html', 
                           cliente=cliente, 
                           bancos=bancos, 
                           contrato=contrato, 
                           data_emissao=data_faturamento,
                           tipo=tipo,
                           forma_de_pagamento_opcoes=forma_de_pagamento_opcoes)

@nfs_bp.route('/nfs')
def listar_nfs():
    today = date.today()
    cliente_id = request.args.get('cliente_id')
    # cliente_id = 1
    print("---------------clinte_id de listar_nfs: ------------", cliente_id)
    clientes = Cliente.query.order_by(asc(Cliente.nome)).all()
    
    if cliente_id:
        nfs = NotaFiscal.query.filter_by(cliente_id=cliente_id).all()
    else:
        nfs = NotaFiscal.query.order_by(desc(NotaFiscal.data_emissao)).all()
    
    return render_template('nfs/nfs_lista.html', nfs=nfs, clientes=clientes, cliente_id=cliente_id, today=today)

@nfs_bp.route('/delete/<int:id>', methods=['POST'])
def delete_nota_fiscal(id):
    """
    Rota para excluir uma Nota Fiscal pelo ID.
    """
    try:
        # Buscar a Nota Fiscal pelo ID
        nota_fiscal = NotaFiscal.query.get(id)

        mov = Movimentacao.query.filter(
                Movimentacao.descricao.startswith(f"NF_{nota_fiscal.numero_nf}")
            ).first()
        print("Entrou em delete: ", mov)

        if nota_fiscal:
            # Excluir a Nota Fiscal e Movimentação
            db.session.delete(nota_fiscal)
            db.session.delete(mov)
            db.session.commit()
            flash(f"Nota Fiscal {id} excluída com sucesso!", "success")
        else:
            flash(f"Nota Fiscal {id} não encontrada.", "error")
    except Exception as e:
        # Reverter transação em caso de erro
        db.session.rollback()
        flash(f"Erro ao tentar excluir a Nota Fiscal: {e}", "error")
    finally:
        db.session.close()

    # Redirecionar de volta para uma página (exemplo: lista de notas fiscais)
    return redirect(url_for('nfs.listar_nfs'))  # Ajuste conforme sua página de lista

@nfs_bp.route('/nfs/atualizar_data_pagamento', methods=['POST'])
def atualizar_data_pagamento():
    data = request.get_json()
    if not data:
        return jsonify(success=False, message="Dados JSON não enviados"), 400
    
    nf_id = data.get('nf_id')
    data_pagamento = data.get('data_usuario') 
    print("------- nf_id: ", nf_id)
    print("------- data_pagamento: ", data_pagamento)

    nf = NotaFiscal.query.get(nf_id)
    mes_emissao = nf.data_emissao.month
    ano_emissao = nf.data_emissao.year

    if not nf:
        return jsonify(success=False, message="Nota Fiscal não encontrada"), 404

    try:
        nf.data_pagamento = data_pagamento
        nf.status_pagamento = 'Recebido'
        db.session.commit()

        print(f"NF_{nf.numero_nf}")
        # 1. Buscar a movimentação
        mov = Movimentacao.query.filter(
            Movimentacao.descricao.startswith(f"NF_{nf.numero_nf}")
        ).first()
        print("Movimentação: ", mov)

        # 2. Atualizar se encontrar
        if mov:
            data_pagamento = datetime.strptime(data_pagamento, '%Y-%m-%d').date()
            mov.data = data_pagamento
            mov.status_pagamento = 'Recebido'
            ''' Foi necessário (conforme mov.mes e mov.ano) reescrever o valor do mes e ano porque em models.py há um
            @event.listens_for(Movimentacao.data, 'set') que sempre que a data é alterada
            há também a alteração do mês e ano, ou seja, quando uma nota é emitida em julho 
            (competencia 7) e paga em agosto, a data recebe a data_pagamento de agosto e o 
            @event alterará o mes para agosto. Para corrigir isso, e não alterar a competência da NF há as 2 linhas abaixo'''
            mov.mes = mes_emissao
            mov.ano = ano_emissao
            db.session.commit()   # salva no banco


        return jsonify(success=True)

    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message=str(e)), 500

@nfs_bp.route('/nfs/<int:nf_id>/cancelar_faturamento', methods=['GET', 'POST'])
def cancelar_faturamento(nf_id):
    nf = NotaFiscal.query.get_or_404(nf_id)
    mov = Movimentacao.query.filter(
            Movimentacao.descricao.startswith(f"NF_{nf.numero_nf}")
        ).first()
    print("Entrou em cancelar faturamento: ", mov)

    if request.method == 'POST':
        nf.data_faturamento = None  # Define como None para cancelar o faturamento

        try:
            db.session.commit()

            # ---- Excluir a Movimentação criada ----
            db.session.delete(mov)
            db.session.commit()


            flash('Nota Fiscal atualizada com sucesso!', 'success')
            return jsonify({'success': True}), 200  # Retorna JSON indicando sucesso
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500  # Retorna JSON com erro

    # Caso seja acessado via GET (não necessário aqui)
    return render_template('nfs/listar_nfs.html', nf=nf)

@nfs_bp.route('/nfs/<int:nf_id>/cancelar_recebimento', methods=['GET', 'POST'])
def cancelar_recebimento(nf_id):
    nf = NotaFiscal.query.get_or_404(nf_id)

    if request.method == 'POST':
        nf.data_pagamento = None  # Define como None para cancelar o recebimento
        nf.status_pagamento = 'No Prazo'

        try:
            db.session.commit()

            print(f"NF_{nf.numero_nf}")
            # 1. Buscar a movimentação
            mov = Movimentacao.query.filter(
                Movimentacao.descricao.startswith(f"NF_{nf.numero_nf}")
            ).first()

            print("Movimentação: ", mov)

            # 2. Atualizar se encontrar
            if mov:
                mov.data = nf.data_vencimento
                mov.status_pagamento = 'Aberto'
                db.session.commit()   # salva no banco


            flash('Nota Fiscal atualizada com sucesso!', 'success')
            return jsonify({'success': True}), 200  # Retorna JSON indicando sucesso
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500  # Retorna JSON com erro

    # Caso seja acessado via GET (não necessário aqui)
    return render_template('nfs/listar_nfs.html', nf=nf)

@nfs_bp.route('/nfs/<int:nf_id>/editar', methods=['GET', 'POST'])
def editar_nf(nf_id):
    nf = NotaFiscal.query.get_or_404(nf_id)
    cliente_id = nf.cliente_id
    cliente = Cliente.query.get_or_404(cliente_id)
    contrato = Contrato.query.get_or_404(nf.contrato_id)
    contrato_numero = contrato.numero_contrato
    
    numero_nf_original = nf.numero_nf
    
    data_emissao_original = nf.data_emissao
    data_vencimento_original = nf.data_vencimento
    forma_de_pagamento_original = nf.forma_de_pagamento

    forma_de_pagamento_opcoes = ['Boleto', 'Pix', 'TED', 'Outros']
    bancos = Banco.query.all()
    

    if request.method == 'POST':
        nf.numero_nf = int(request.form['numero_nf'])
        print(f"NFs: Original - {numero_nf_original} Novo Número: {int(request.form['numero_nf'])}")
        nf.data_emissao = datetime.strptime(request.form['data_emissao'], '%Y-%m-%d').date()
        nf.valor_bruto = float(request.form['valor_bruto'])
        nf.valor_liquido = float(request.form['valor_liquido'])
        nf.forma_de_pagamento = request.form['forma_de_pagamento']
        nf.banco_id = int(request.form['banco_id'])
        nf.data_vencimento = datetime.strptime(request.form['data_vencimento'], '%Y-%m-%d').date()
        nf.boleto = request.form['boleto']
        nf.observacao = request.form['observacao']

        try:
            db.session.commit()

            print(f"nf_original: NF_{numero_nf_original}. Entrou no Try!")
            # 1. Buscar a movimentação
            print(f"Filtro - começa com: NF_{numero_nf_original}")
            mov = Movimentacao.query.filter(
                Movimentacao.descricao.startswith(f"NF_{numero_nf_original}")
            ).first()

            print("Movimentação filtrada: ", mov)

            # 2. Atualizar se encontrar
            if mov:
                nf = NotaFiscal.query.get_or_404(nf_id)
                if nf.data_emissao != data_emissao_original:
                    print("Datas de emissão diferentes!")
                    mov.mes = nf.data_emissao.month,  # 1-12
                    mov.ano = nf.data_emissao.year,  # 2024, 2025, etc.
                if nf.numero_nf != numero_nf_original:
                    print("Número da NF diferentes!")
                    # descricao = f"NF_{nf.numero_nf}_Cliente_{cliente.nome}_Contrato_{contrato.numero_contrato}"
                    partes = mov.descricao.split('_')
                    print(f"Partes: {partes}")
                    partes[1] = str(nf.numero_nf)
                    print(f"Partes: {partes[1]}")
                    print(f"Nova Descrição: {'_'.join(partes)}")
                    mov.descricao = '_'.join(partes)
                if nf.data_vencimento != data_vencimento_original:
                    print("Datas de vencimento diferentes!")
                    mov.data = nf.data_vencimento
                if nf.forma_de_pagamento != forma_de_pagamento_original:
                    print("Forma de pagamento diferentes!")
                    mov.forma_de_pagamento = nf.forma_de_pagamento

                mov.observacao = 'Tipo de Serviço: ' + nf.tipo_servico + ' - ' + nf.observacao

                db.session.commit()   # salva no banco

            if nf.tipo_servico == 'Assinatura':
                contrato.data_faturamento_assinatura = datetime.strptime(request.form['data_emissao'], '%Y-%m-%d').date()
            elif nf.tipo_servico == 'Protocolo':
                contrato.data_faturamento_protocolo = datetime.strptime(request.form['data_emissao'], '%Y-%m-%d').date()
            else:
                contrato.data_faturamento_aprovacao = datetime.strptime(request.form['data_emissao'], '%Y-%m-%d').date()
            db.session.commit()
            
            flash('Nota Fiscal editada com sucesso!', 'success')
            return redirect(url_for('nfs.listar_nfs'))
            # return jsonify({'success': True}), 200  # Retorna JSON indicando sucesso
        except Exception as e:
            flash('Erro inesperado ao salvar: ' + str(e), 'danger')
            # db.session.rollback()
            # return jsonify({'success': False, 'message': str(e)}), 500  # Retorna JSON com erro
        
    return render_template('nfs/nf_editar.html', 
                           nf = nf,
                           cliente=cliente,
                           bancos=bancos,
                           contrato=contrato_numero,
                           forma_de_pagamento_opcoes=forma_de_pagamento_opcoes                     
                           )