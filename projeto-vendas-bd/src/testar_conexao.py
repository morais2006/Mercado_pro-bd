"""
testar_conexao.py
Script auxiliar para checar se o banco está pronto antes de rodar o Flask.

Rode da raiz do projeto:
    python src/testar_conexao.py

O script:
  1. Conecta no banco usando a DATABASE_URL do .env
  2. Roda SELECT 1
  3. Verifica se existem no banco:
     - as 4 tabelas (clientes, produtos, vendas, itens_venda)
     - a VIEW vw_relatorio_vendas
     - a FUNCTION fn_total_venda
     - a PROCEDURE sp_realizar_venda
  4. Mostra um relatório OK / FALTANDO
"""

import sys
import db


TABELAS = ["clientes", "produtos", "vendas", "itens_venda"]
VIEW = "vw_relatorio_vendas"
FUNCAO = "fn_total_venda"
PROCEDURE = "sp_realizar_venda"


def _marca(ok):
    return "OK      " if ok else "FALTANDO"


def main():
    print("== Teste de conexão com o banco ==\n")

    # 1) Conexão + SELECT 1
    try:
        linha = db.fetch_one("SELECT 1 AS ok")
    except db.ConfiguracaoBancoInvalida as e:
        print("[X] Falha de configuração:")
        print("   ", e)
        sys.exit(1)
    except Exception as e:
        print("[X] Erro inesperado ao conectar:", e)
        sys.exit(1)

    print(f"[OK] Conectado. SELECT 1 retornou: {linha}\n")

    # 2) Verifica tabelas
    print("Tabelas:")
    faltando = []
    for t in TABELAS:
        r = db.fetch_one(
            """
            SELECT 1 FROM information_schema.tables
             WHERE table_schema = 'public' AND table_name = %s
            """,
            (t,),
        )
        existe = r is not None
        print(f"  {_marca(existe)}  {t}")
        if not existe:
            faltando.append(("tabela", t))

    # 3) VIEW
    r = db.fetch_one(
        """
        SELECT 1 FROM information_schema.views
         WHERE table_schema = 'public' AND table_name = %s
        """,
        (VIEW,),
    )
    print(f"\nView:\n  {_marca(r is not None)}  {VIEW}")
    if r is None:
        faltando.append(("view", VIEW))

    # 4) FUNCTION
    r = db.fetch_one(
        """
        SELECT 1 FROM pg_proc p
          JOIN pg_namespace n ON n.oid = p.pronamespace
         WHERE n.nspname = 'public'
           AND p.proname = %s
           AND p.prokind = 'f'
        """,
        (FUNCAO,),
    )
    print(f"\nFunction:\n  {_marca(r is not None)}  {FUNCAO}")
    if r is None:
        faltando.append(("function", FUNCAO))

    # 5) PROCEDURE
    r = db.fetch_one(
        """
        SELECT 1 FROM pg_proc p
          JOIN pg_namespace n ON n.oid = p.pronamespace
         WHERE n.nspname = 'public'
           AND p.proname = %s
           AND p.prokind = 'p'
        """,
        (PROCEDURE,),
    )
    print(f"\nProcedure:\n  {_marca(r is not None)}  {PROCEDURE}")
    if r is None:
        faltando.append(("procedure", PROCEDURE))

    # Resumo
    print("\n== Resumo ==")
    if not faltando:
        print("Tudo pronto. Pode rodar: python src/app.py")
    else:
        print("Faltam os seguintes objetos no banco:")
        for tipo, nome in faltando:
            print(f"  - {tipo}: {nome}")
        print("\nConecte-se ao banco (psql ou pgAdmin) e rode os scripts na ordem:")
        print("  1. database/tables/01_criar_tabelas.sql")
        print("  2. database/views/02_vw_relatorio_vendas.sql")
        print("  3. database/functions/03_fn_total_venda.sql")
        print("  4. database/procedures/04_sp_realizar_venda.sql")
        print("  5. database/inserts/05_dados_exemplo.sql")
        sys.exit(2)


if __name__ == "__main__":
    main()
