
CREATE TABLE IF NOT EXISTS backup_cisternas SELECT * FROM cisternas WHERE 1=0;
INSERT INTO backup_cisternas SELECT * FROM cisternas;

CREATE TABLE IF NOT EXISTS backup_comunicados_gerais SELECT * FROM comunicados_gerais WHERE 1=0;
INSERT INTO backup_comunicados_gerais SELECT * FROM comunicados_gerais;

CREATE TABLE IF NOT EXISTS backup_comunicado_pedido SELECT * FROM comunicado_pedido WHERE 1=0;
INSERT INTO backup_comunicado_pedido SELECT * FROM comunicado_pedido;

CREATE TABLE IF NOT EXISTS backup_configuracoes_sistema SELECT * FROM configuracoes_sistema WHERE 1=0;
INSERT INTO backup_configuracoes_sistema SELECT * FROM configuracoes_sistema;

CREATE TABLE IF NOT EXISTS backup_dispositivos SELECT * FROM dispositivos WHERE 1=0;
INSERT INTO backup_dispositivos SELECT * FROM dispositivos;

CREATE TABLE IF NOT EXISTS backup_empresas SELECT * FROM empresas WHERE 1=0;
INSERT INTO backup_empresas SELECT * FROM empresas;

CREATE TABLE IF NOT EXISTS backup_pedidos SELECT * FROM pedidos WHERE 1=0;
INSERT INTO backup_pedidos SELECT * FROM pedidos;

CREATE TABLE IF NOT EXISTS backup_pedidos_empresas SELECT * FROM pedidos_empresas WHERE 1=0;
INSERT INTO backup_pedidos_empresas SELECT * FROM pedidos_empresas;

CREATE TABLE IF NOT EXISTS backup_niveis_agua_cisterna SELECT * FROM niveis_agua_cisterna WHERE 1=0;
INSERT INTO backup_niveis_agua_cisterna SELECT * FROM niveis_agua_cisterna;

CREATE TABLE IF NOT EXISTS backup_ph_niveis_cisterna SELECT * FROM ph_niveis_cisterna WHERE 1=0;
INSERT INTO backup_ph_niveis_cisterna SELECT * FROM ph_niveis_cisterna;


DROP TABLE IF EXISTS cisternas;
DROP TABLE IF EXISTS comunicados_gerais;
DROP TABLE IF EXISTS comunicado_pedido;
DROP TABLE IF EXISTS configuracoes_sistema;
DROP TABLE IF EXISTS dispositivos;
DROP TABLE IF EXISTS empresas;
DROP TABLE IF EXISTS pedidos;
DROP TABLE IF EXISTS pedidos_empresas;
DROP TABLE IF EXISTS niveis_agua_cisterna;
DROP TABLE IF EXISTS ph_niveis_cisterna;

-- Observação: tabelas em uso atual (não dropar):
-- usuarios, admins, configuracoes, locais, ph_niveis, niveis_agua, notificacoes, notificacoes_admin
-- leituras, umidade_niveis, boia_niveis, estados_luz
-- sensores, sensores_locais, sensores_tipos    