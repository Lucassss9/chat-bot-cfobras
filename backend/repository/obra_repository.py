import base64
from model.colaborador_model import Colaborador
from model.obra_model import SolicitacaoObra, PessoaDaObra, ObraExtra
from model.usuario_model import Usuario
from service.texto_util import normalizar_nome, normalizar_email

LIMITE_PDF = 5 * 1024 * 1024   # 5 MB

def salvar(dados, solicitante_id, db):
    try:
        arquivo = None
        if dados.ficha_base64:
            arquivo = base64.b64decode(dados.ficha_base64)
            if len(arquivo) > LIMITE_PDF:
                raise ValueError("A ficha cadastral passa de 5 MB.")

        solicitacao = SolicitacaoObra(
            estado=dados.estado,
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
            obra_cep=getattr(dados, "obra_cep", None),
            tel_adm=getattr(dados, "tel_adm", None),
            tel_engenheiro=getattr(dados, "tel_engenheiro", None),
            ficha_nome=dados.ficha_nome,
            ficha_arquivo=arquivo,
            solicitante_id=solicitante_id,
        )

        for pessoa in dados.pessoas:
            solicitacao.pessoas.append(PessoaDaObra(
                nome=normalizar_nome(pessoa.nome),
                email=normalizar_email(pessoa.email),
                funcao=None if pessoa.ja_tem_acesso else pessoa.funcao,
                cpf=None if pessoa.ja_tem_acesso else pessoa.cpf,
                terceirizado=False if pessoa.ja_tem_acesso else pessoa.terceirizado,
                ja_tem_acesso=pessoa.ja_tem_acesso,
            ))

        for extra in getattr(dados, "obras_extras", []) or []:
            solicitacao.obras_extras.append(ObraExtra(
                obra_nome=extra.obra_nome,
                obra_codigo=extra.obra_codigo,
                obra_email=extra.obra_email,
                obra_endereco=extra.obra_endereco,
                obra_cidade=extra.obra_cidade,
                obra_estado=extra.obra_estado,
                obra_engenheiro=extra.obra_engenheiro,
                obra_descricao=extra.obra_descricao,
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


def editar_e_reenviar(solicitacao_id, dados, solicitante_id, db, eh_admin=False):
    """Atualiza os dados da solicitacao de obra e volta para pendente.
    Solicitante so edita a sua e so se recusada; admin edita qualquer uma."""
    try:
        s = buscar_por_id(solicitacao_id, db)
        if s is None:
            return "nao_encontrado"
        if not eh_admin:
            if s.solicitante_id != solicitante_id:
                return "nao_e_seu"
            if s.status != "recusado":
                return "nao_recusado"

        s.estado = dados.estado
        s.tipo_filial = dados.tipo_filial
        s.filial_nome = dados.filial_nome
        s.filial_cnpj = dados.filial_cnpj
        s.filial_endereco = dados.filial_endereco
        s.filial_cidade = dados.filial_cidade
        s.filial_estado = dados.filial_estado
        s.obra_nome = dados.obra_nome
        s.obra_codigo = dados.obra_codigo
        s.obra_email = dados.obra_email
        s.obra_endereco = dados.obra_endereco
        s.obra_cidade = dados.obra_cidade
        s.obra_estado = dados.obra_estado
        s.obra_engenheiro = dados.obra_engenheiro
        s.obra_descricao = dados.obra_descricao
        s.obra_cep = getattr(dados, "obra_cep", None)
        s.tel_adm = getattr(dados, "tel_adm", None)
        s.tel_engenheiro = getattr(dados, "tel_engenheiro", None)

        if dados.ficha_base64:
            arquivo = base64.b64decode(dados.ficha_base64)
            if len(arquivo) > LIMITE_PDF:
                raise ValueError("A ficha cadastral passa de 5 MB.")
            s.ficha_nome = dados.ficha_nome
            s.ficha_arquivo = arquivo

        s.pessoas.clear()
        for pessoa in dados.pessoas:
            s.pessoas.append(PessoaDaObra(
                nome=normalizar_nome(pessoa.nome),
                email=normalizar_email(pessoa.email),
                funcao=None if pessoa.ja_tem_acesso else pessoa.funcao,
                cpf=None if pessoa.ja_tem_acesso else pessoa.cpf,
                terceirizado=False if pessoa.ja_tem_acesso else pessoa.terceirizado,
                ja_tem_acesso=pessoa.ja_tem_acesso,
            ))

        s.obras_extras.clear()
        for extra in getattr(dados, "obras_extras", []) or []:
            s.obras_extras.append(ObraExtra(
                obra_nome=extra.obra_nome,
                obra_codigo=extra.obra_codigo,
                obra_email=extra.obra_email,
                obra_endereco=extra.obra_endereco,
                obra_cidade=extra.obra_cidade,
                obra_estado=extra.obra_estado,
                obra_engenheiro=extra.obra_engenheiro,
                obra_descricao=extra.obra_descricao,
            ))

        s.status = "pendente"
        s.motivo = None
        db.commit()
        db.refresh(s)
        return s
    except Exception:
        db.rollback()
        raise


def criar_colaboradores_da_obra(solicitacao, db):
    """Cada pessoa da obra vira uma solicitacao de colaborador (pendente)."""
    obra_texto = solicitacao.obra_nome or solicitacao.filial_nome or ""
    obs = f"Da solicitacao de obra: {solicitacao.filial_nome}"
    for p in solicitacao.pessoas:
        col = Colaborador(
            nome=p.nome,
            email=p.email,
            funcao=None if p.ja_tem_acesso else p.funcao,
            estado=solicitacao.estado,
            obra=obra_texto,
            observacao=obs,
            terceirizado=False if p.ja_tem_acesso else p.terceirizado,
            ja_tem_acesso=p.ja_tem_acesso,
            cpf=None if p.ja_tem_acesso else p.cpf,
            status="cadastrado" if p.ja_tem_acesso else "pendente",
            solicitante_id=solicitacao.solicitante_id,
        )
        db.add(col)
    db.commit()