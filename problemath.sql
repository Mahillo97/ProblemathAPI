-- MySQL dump 10.13  Distrib 8.0.19, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: problemath
-- ------------------------------------------------------
-- Server version	8.0.19

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
-- Table structure for table `dependency`
--

DROP TABLE IF EXISTS `dependency`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dependency` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `Id_Problem` int DEFAULT NULL,
  `Id_Solu` int DEFAULT NULL,
  `URL` varchar(100) NOT NULL,
  PRIMARY KEY (`Id`),
  KEY `FK_DEPENDENCY_PROBLEM_idx` (`Id_Problem`),
  KEY `FK_DEPENDENCY_SOLUTION_idx` (`Id_Solu`),
  CONSTRAINT `FK_DEPENDENCY_PROBLEM` FOREIGN KEY (`Id_Problem`) REFERENCES `problem` (`Id`),
  CONSTRAINT `FK_DEPENDENCY_SOLUTION` FOREIGN KEY (`Id_Solu`) REFERENCES `solution` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `problem`
--

DROP TABLE IF EXISTS `problem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `problem` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `Tags` varchar(200) NOT NULL,
  `Magacine` varchar(100) DEFAULT NULL,
  `Tex` mediumtext NOT NULL,
  `Proposer` varchar(50) DEFAULT NULL,
  `Dep_State` tinyint NOT NULL,
  `URL_PDF_State` varchar(100) NOT NULL,
  `URL_PDF_Full` varchar(100) NOT NULL,
  PRIMARY KEY (`Id`),
  UNIQUE KEY `URL_PDF_State_UNIQUE` (`URL_PDF_State`),
  UNIQUE KEY `URL_PDF_Full_UNIQUE` (`URL_PDF_Full`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `solution`
--

DROP TABLE IF EXISTS `solution`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `solution` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `Id_Problem` int NOT NULL,
  `Tex` mediumtext NOT NULL,
  `Solver` varchar(50) DEFAULT NULL,
  `Dep_Solu` tinyint NOT NULL,
  PRIMARY KEY (`Id`),
  KEY `FK_SOLUTION_PROBLEM_idx` (`Id_Problem`),
  CONSTRAINT `FK_SOLUTION_PROBLEM` FOREIGN KEY (`Id_Problem`) REFERENCES `problem` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(20) NOT NULL,
  `password` char(40) NOT NULL,
  PRIMARY KEY (`Id`),
  UNIQUE KEY `username_UNIQUE` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-04-14 10:51:06
