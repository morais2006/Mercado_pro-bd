-- 00_criar_banco.sql
-- Script OPCIONAL — rode UMA VEZ no 'psql' conectado como superusuário
-- (geralmente o usuário 'postgres'), antes dos demais scripts.
-- Ele apenas cria o banco de dados vazio chamado 'mercado_pro'.
--
-- Comandos equivalentes no terminal:
--   psql -U postgres -c "CREATE DATABASE mercado_pro;"

CREATE DATABASE mercado_pro
    WITH ENCODING = 'UTF8'
         LC_COLLATE = 'pt_BR.UTF-8'
         LC_CTYPE   = 'pt_BR.UTF-8'
         TEMPLATE   = template0;

-- Depois disso, conecte-se ao novo banco:
--   psql -U postgres -d mercado_pro
-- e execute os scripts 01 ... 05 na ordem.
