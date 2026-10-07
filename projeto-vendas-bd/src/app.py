"""
app.py
Aplicação Flask do sistema de vendas.
Telas: Clientes, Produtos, Nova venda, Relatório de vendas, Detalhe da venda.
Usa diretamente a VIEW vw_relatorio_vendas, a FUNCTION fn_total_venda
e a PROCEDURE sp_realizar_venda.
"""

import json
from flask import Flask, render_template, request, redirect, url_for, flash

import db
from db import ConfiguracaoBancoInvalida, DatabaseError

app = Flask(__name__)
app.secret_key = "troque-esta-chave-em-producao"


# Página amigável quando o .env está errado ou o banco não responde.
@app.errorhandler(ConfiguracaoBancoInvalida)
def _erro_config_banco(e):
    return render_template("erro_banco.html", mensagem=str(e)), 500


# =============================================================
# Página inicial
# =============================================================
@app.route("/")
def index():
    return render_template("index.html")


# =============================================================
# CLIENTES
# =============================================================
@app.route("/clientes")
def listar_clientes():
    clientes = db.fetch_all(
        "SELECT id, nome, email, telefone, criado_em FROM clientes ORDER BY nome"
    )
    return render_template("clientes_listar.html", clientes=clientes)


@app.route("/clientes/novo", methods=["GET", "POST"])
def novo_cliente():
    if request.method == "POST":
        try:
            db.execute(
                "INSERT INTO clientes (nome, email, telefone) VALUES (%s, %s, %s)",
                (
                    request.form["nome"].strip(),
                    request.form["email"].strip(),
                    request.form["telefone"].strip(),
                ),
            )
            flash("Cliente cadastrado com sucesso.", "sucesso")
            return redirect(url_for("listar_clientes"))
        except Exception as e:
            flash(f"Erro ao cadastrar cliente: {e}", "erro")
    return render_template("cliente_form.html", cliente=None)


@app.route("/clientes/<int:id_cliente>/editar", methods=["GET", "POST"])
def editar_cliente(id_cliente):
    if request.method == "POST":
        try:
            db.execute(
                "UPDATE clientes SET nome=%s, email=%s, telefone=%s WHERE id=%s",
                (
                    request.form["nome"].strip(),
                    request.form["email"].strip(),
                    request.form["telefone"].strip(),
                    id_cliente,
                ),
            )
            flash("Cliente atualizado.", "sucesso")
            return redirect(url_for("listar_clientes"))
        except Exception as e:
            flash(f"Erro ao atualizar cliente: {e}", "erro")

    cliente = db.fetch_one(
        "SELECT id, nome, email, telefone FROM clientes WHERE id=%s", (id_cliente,)
    )
    if not cliente:
        flash("Cliente não encontrado.", "erro")
        return redirect(url_for("listar_clientes"))
    return render_template("cliente_form.html", cliente=cliente)


@app.route("/clientes/<int:id_cliente>/excluir", methods=["POST"])
def excluir_cliente(id_cliente):
    try:
        db.execute("DELETE FROM clientes WHERE id=%s", (id_cliente,))
        flash("Cliente excluído.", "sucesso")
    except Exception as e:
        flash(f"Não foi possível excluir (talvez possua vendas): {e}", "erro")
    return redirect(url_for("listar_clientes"))


# =============================================================
# PRODUTOS
# =============================================================
@app.route("/produtos")
def listar_produtos():
    produtos = db.fetch_all(
        "SELECT id, nome, preco, estoque FROM produtos ORDER BY nome"
    )
    return render_template("produtos_listar.html", produtos=produtos)


@app.route("/produtos/novo", methods=["GET", "POST"])
def novo_produto():
    if request.method == "POST":
        try:
            db.execute(
                "INSERT INTO produtos (nome, preco, estoque) VALUES (%s, %s, %s)",
                (
                    request.form["nome"].strip(),
                    request.form["preco"],
                    request.form["estoque"],
                ),
            )
            flash("Produto cadastrado.", "sucesso")
            return redirect(url_for("listar_produtos"))
        except Exception as e:
            flash(f"Erro ao cadastrar produto: {e}", "erro")
    return render_template("produto_form.html", produto=None)


@app.route("/produtos/<int:id_produto>/editar", methods=["GET", "POST"])
def editar_produto(id_produto):
    if request.method == "POST":
        try:
            db.execute(
                "UPDATE produtos SET nome=%s, preco=%s, estoque=%s WHERE id=%s",
                (
                    request.form["nome"].strip(),
                    request.form["preco"],
                    request.form["estoque"],
                    id_produto,
                ),
            )
            flash("Produto atualizado.", "sucesso")
            return redirect(url_for("listar_produtos"))
        except Exception as e:
            flash(f"Erro ao atualizar produto: {e}", "erro")

    produto = db.fetch_one(
        "SELECT id, nome, preco, estoque FROM produtos WHERE id=%s", (id_produto,)
    )
    if not produto:
        flash("Produto não encontrado.", "erro")
        return redirect(url_for("listar_produtos"))
    return render_template("produto_form.html", produto=produto)


@app.route("/produtos/<int:id_produto>/excluir", methods=["POST"])
def excluir_produto(id_produto):
    try:
        db.execute("DELETE FROM produtos WHERE id=%s", (id_produto,))
        flash("Produto excluído.", "sucesso")
    except Exception as e:
        flash(f"Não foi possível excluir (talvez esteja em alguma venda): {e}", "erro")
    return redirect(url_for("listar_produtos"))


# =============================================================
# NOVA VENDA (usa a PROCEDURE sp_realizar_venda via CALL)
# =============================================================
@app.route("/vendas/nova", methods=["GET", "POST"])
def nova_venda():
    clientes = db.fetch_all("SELECT id, nome FROM clientes ORDER BY nome")
    produtos = db.fetch_all(
        "SELECT id, nome, preco, estoque FROM produtos ORDER BY nome"
    )

    if request.method == "POST":
        try:
            id_cliente = int(request.form["id_cliente"])
            desconto = float(request.form.get("desconto") or 0)

            # As linhas do formulário vêm como listas paralelas
            ids_produto = request.form.getlist("id_produto")
            quantidades = request.form.getlist("quantidade")

            itens = []
            for pid, qtd in zip(ids_produto, quantidades):
                if pid and qtd and int(qtd) > 0:
                    itens.append({"id_produto": int(pid), "quantidade": int(qtd)})

            if not itens:
                flash("Adicione pelo menos um item à venda.", "erro")
                return render_template(
                    "venda_nova.html", clientes=clientes, produtos=produtos
                )

            # Chama a PROCEDURE. Se a procedure lançar exceção,
            # o driver propaga DatabaseError e fazemos rollback.
            db.call_procedure(
                "sp_realizar_venda",
                (id_cliente, json.dumps(itens), desconto),
            )
            flash("Venda realizada com sucesso!", "sucesso")
            return redirect(url_for("relatorio_vendas"))

        except DatabaseError as e:
            # Mensagem amigável vinda da procedure (RAISE EXCEPTION)
            mensagem = str(e).strip().splitlines()[0]
            flash(f"Não foi possível registrar a venda: {mensagem}", "erro")
        except Exception as e:
            flash(f"Erro inesperado: {e}", "erro")

    return render_template("venda_nova.html", clientes=clientes, produtos=produtos)


# =============================================================
# RELATÓRIO DE VENDAS (usa a VIEW vw_relatorio_vendas)
# =============================================================
@app.route("/vendas")
def relatorio_vendas():
    vendas = db.fetch_all(
        """
        SELECT id_venda, data_venda, nome_cliente, quantidade_itens, subtotal
          FROM vw_relatorio_vendas
        """
    )
    return render_template("vendas_relatorio.html", vendas=vendas)


# =============================================================
# DETALHE DA VENDA (usa a FUNCTION fn_total_venda)
# =============================================================
@app.route("/vendas/<int:id_venda>")
def detalhe_venda(id_venda):
    venda = db.fetch_one(
        """
        SELECT v.id, v.data_venda, v.desconto_percentual,
               c.nome AS nome_cliente, c.email AS email_cliente
          FROM vendas v
          JOIN clientes c ON c.id = v.id_cliente
         WHERE v.id = %s
        """,
        (id_venda,),
    )
    if not venda:
        flash("Venda não encontrada.", "erro")
        return redirect(url_for("relatorio_vendas"))

    itens = db.fetch_all(
        """
        SELECT i.quantidade, i.preco_unitario,
               p.nome AS nome_produto,
               (i.quantidade * i.preco_unitario) AS subtotal_item
          FROM itens_venda i
          JOIN produtos p ON p.id = i.id_produto
         WHERE i.id_venda = %s
         ORDER BY p.nome
        """,
        (id_venda,),
    )

    # Chama a FUNCTION fn_total_venda(id)
    total_row = db.fetch_one(
        "SELECT fn_total_venda(%s) AS total", (id_venda,)
    )
    total = total_row["total"] if total_row else 0

    return render_template(
        "venda_detalhe.html", venda=venda, itens=itens, total=total
    )


if __name__ == "__main__":
    app.run(debug=True)
