import base64
from model.obra_model import SolicitacaoObra, PessoaDaObra
from model.usuario_model import Usuario

LIMITE_PDF = 5 * 1024 * 1024   # 5 MB


def salvar(dados, solicitante_id, db):
    try:
        arquivo = None
        if dados.ficha_base64:
            arquivo = base64.b64decode(dados.ficha_base64)
            if len(arquivo) > LIMITE_PDF:
                raise ValueError("A ficha cadastral passa de 5 MB.")

        solicitacao = SolicitacaoObra(
            tipo_filial=dados.tipo_filial,
            filial_nome=dados.filial_nome,
            filial_cnpj=dados.filial_cnpj,
            filial_endereco=dados.filial_endereco,
            filial_cidade=dados.filial_cidade,
            filial_estado=dados.filial_estado,
            obra_nome=dados.obra_nome,
            obra_codigo=dados.obra_codigo,
            obra_email=dados.obra_email,
            obra_endereco=dados.obra_endereco,
            obra_cidade=dados.obra_cidade,
            obra_estado=dados.obra_estado,
            obra_engenheiro=dados.obra_engenheiro,
            obra_descricao=dados.obra_descricao,
            ficha_nome=dados.ficha_nome,
            ficha_arquivo=arquivo,
            solicitante_id=solicitante_id,
        )

        for pessoa in dados.pessoas:
            solicitacao.pessoas.append(PessoaDaObra(
                nome=pessoa.nome,
                email=pessoa.email,
                funcao=pessoa.funcao,
                tipo=pessoa.tipo,
                ja_tem_acesso=pessoa.ja_tem_acesso,
            ))

        db.add(solicitacao)
        db.commit()
        db.refresh(solicitacao)
        return solicitacao

    except Exception:
        db.rollback()
        raise


def buscar_por_id(solicitacao_id, db):
    return db.query(SolicitacaoObra).filter(SolicitacaoObra.id == solicitacao_id).first()


def listar_todas(db):
    resultados = (db.query(SolicitacaoObra, Usuario.nome)
                  .outerjoin(Usuario, SolicitacaoObra.solicitante_id == Usuario.id)
                  .order_by(SolicitacaoObra.criado_em.desc())
                  .all())

    lista = []
    for solicitacao, nome_do_solicitante in resultados:
        solicitacao.solicitante_nome = nome_do_solicitante
        lista.append(solicitacao)
    return lista


def listar_do_solicitante(solicitante_id, db):
    return (db.query(SolicitacaoObra)
            .filter(SolicitacaoObra.solicitante_id == solicitante_id)
            .order_by(SolicitacaoObra.criado_em.desc())
            .all())


def atualizar_decisao(solicitacao_id, status, motivo, db):
    try:
        solicitacao = buscar_por_id(solicitacao_id, db)
        if solicitacao is None:
            return None
        solicitacao.status = status
        solicitacao.motivo = motivo
        db.commit()
        db.refresh(solicitacao)
        return solicitacao
    except Exception:
        db.rollback()
        raise