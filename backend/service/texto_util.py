MINUSCULAS = {"de", "da", "do", "das", "dos", "e", "di", "du", "a", "o"}


def normalizar_nome(nome):
    if not nome:
        return nome

    palavras = nome.strip().split()
    resultado = []
    for i, palavra in enumerate(palavras):
        minuscula = palavra.lower()
        if i > 0 and minuscula in MINUSCULAS:
            resultado.append(minuscula)
        else:
            resultado.append(minuscula.capitalize())
    return " ".join(resultado)


def normalizar_email(email):
    if not email:
        return email
    return email.strip().lower()