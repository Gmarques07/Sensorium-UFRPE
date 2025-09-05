-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: banco_de_dados
-- ------------------------------------------------------
-- Server version	9.1.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `endereco` varchar(200) NOT NULL,
  `senha_hash` varchar(255) NOT NULL,
  `ativo` tinyint(1) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_usuarios_email` (`email`),
  KEY `ix_usuarios_id` (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'Teste Usuario','teste_local@example.com','Rua Teste, 123','$2b$12$qRutobVrzL9.LOZgluJnJ.zqGfGfh5qaE7Z6874/bifyYR4f/Opl.',1,'2025-08-30 00:09:25',NULL),(2,'gabriel','emaisl@hotrmai.com','rua123','$2b$12$yKQDTqi85d/xLzqFXW92NewwugKd8dN3D0ge1j/3gnLQcpmm6meLW',1,'2025-08-30 00:10:20',NULL),(3,'Gabrielllx','teste@gmail.com','rua 123','$2b$12$lmXMp5V1yFHXMXJLGxygNuZaOatVOqJVEwSgEE7eKrxMcv5h/Trgi',1,'2025-09-02 21:02:17',NULL),(4,'luis','asadsk@hotmail.com','rua121121','$2b$12$7zFYDZskqzbWrSdn8eY7ReCPTn/D56HZuWEZqDLJGIcZflDH6Uz.G',1,'2025-09-02 21:26:33',NULL),(5,'luis','asksaka@hotmail.com','rau12212','$2b$12$kspCy7KffNCQ3Bszu68vOum.WSc1ZS1X0.5cqpCVVzCCjWdOIncpC',1,'2025-09-02 21:48:37',NULL),(6,'kdaskdsakk','sakdakask@hotmail.com','rau1212','$2b$12$2IGEfxoARenuFniczApiKuUYXY79vXH6WuR1pcbGJ/3zSnBsaY9.W',1,'2025-09-02 22:40:50',NULL),(7,'teste','teste@teste.com','teste ','$2b$12$joW5YS0Yl5JtU.0BZ1NCWOPVdnfwWFiWdyROBtAtPqa.bCnNH2KV2',1,'2025-09-04 20:53:56',NULL);
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-05 13:01:15
