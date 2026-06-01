from database.manual_model import Manual
from database.connection import session_local
from service.notion_service import buscar_pagina

session = session_local()

manual = Manual(conteudo=buscar_pagina())
session.add(manual)
session.commit()
session.close()