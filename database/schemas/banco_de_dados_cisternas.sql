CREATE TABLE IF NOT EXISTS cisternas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    tipo_equipamento ENUM('arduino', 'raspberry') NOT NULL,
    data_instalacao DATETIME NOT NULL,
    status ENUM('ativo', 'inativo', 'manutencao') NOT NULL DEFAULT 'ativo',
    cpf_usuario VARCHAR(11) NOT NULL,
    cnpj_empresa VARCHAR(14) NOT NULL,
    dispositivo_id VARCHAR(50) NULL,
    FOREIGN KEY (cpf_usuario) REFERENCES usuarios(cpf) ON DELETE CASCADE,
    FOREIGN KEY (cnpj_empresa) REFERENCES empresas(cnpj) ON DELETE CASCADE,
    FOREIGN KEY (dispositivo_id) REFERENCES dispositivos(id)
);

-- Tabela para associar leituras de pH a cisternas específicas
CREATE TABLE IF NOT EXISTS ph_niveis_cisterna (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cisterna_id INT NOT NULL,
    ph DECIMAL(4,2) NOT NULL,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cisterna_id) REFERENCES cisternas(id) ON DELETE CASCADE
);

-- Tabela para associar níveis de água a cisternas específicas
CREATE TABLE IF NOT EXISTS niveis_agua_cisterna (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cisterna_id INT NOT NULL,
    boia DECIMAL(5,2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cisterna_id) REFERENCES cisternas(id) ON DELETE CASCADE
);

-- Tabela para armazenar os dispositivos IoT
CREATE TABLE IF NOT EXISTS dispositivos (
    id VARCHAR(50) PRIMARY KEY,
    tipo_equipamento ENUM('arduino', 'raspberry') NOT NULL,
    status ENUM('disponivel', 'em_uso', 'manutencao') DEFAULT 'disponivel',
    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultima_comunicacao TIMESTAMP NULL
);

-- Removendo a restrição UNIQUE do identificador antigo
ALTER TABLE cisternas DROP INDEX identificador; 