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
  `URL` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`Id`),
  KEY `FK_DEPENDENCY_PROBLEM_idx` (`Id_Problem`),
  KEY `FK_DEPENDENCY_SOLUTION_idx` (`Id_Solu`),
  CONSTRAINT `FK_DEPENDENCY_PROBLEM` FOREIGN KEY (`Id_Problem`) REFERENCES `problem` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_DEPENDENCY_SOLUTION` FOREIGN KEY (`Id_Solu`) REFERENCES `solution` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dependency`
--

LOCK TABLES `dependency` WRITE;
/*!40000 ALTER TABLE `dependency` DISABLE KEYS */;
/*!40000 ALTER TABLE `dependency` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `problem`
--

DROP TABLE IF EXISTS `problem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `problem` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `Magazine` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `Tex` mediumtext COLLATE utf8mb4_general_ci NOT NULL,
  `Proposer` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `Dep_State` tinyint NOT NULL,
  `URL_PDF_State` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `URL_PDF_Full` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`Id`),
  UNIQUE KEY `URL_PDF_State_UNIQUE` (`URL_PDF_State`),
  UNIQUE KEY `URL_PDF_Full_UNIQUE` (`URL_PDF_Full`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `problem`
--

LOCK TABLES `problem` WRITE;
/*!40000 ALTER TABLE `problem` DISABLE KEYS */;
INSERT INTO `problem` VALUES (1,NULL,'tex','Ciaurri',0,'url.pdf','url2.pdf'),(2,'Gaceta','tex2','Mahillo',1,'ur3l.pdf','url4.pdf'),(3,NULL,'tex',NULL,0,'url','url7.pdf');
/*!40000 ALTER TABLE `problem` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `problem_tag`
--

DROP TABLE IF EXISTS `problem_tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `problem_tag` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `Id_Problem` int NOT NULL,
  `Id_Tag` int NOT NULL,
  PRIMARY KEY (`Id`),
  KEY `FK_PROBLEM_TAG_PROBLEM_idx` (`Id_Problem`),
  KEY `FK_PROBLEM_TAG_TAG_idx` (`Id_Tag`),
  CONSTRAINT `FK_PROBLEM_TAG_PROBLEM` FOREIGN KEY (`Id_Problem`) REFERENCES `problem` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_PROBLEM_TAG_TAG` FOREIGN KEY (`Id_Tag`) REFERENCES `tag` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `problem_tag`
--

LOCK TABLES `problem_tag` WRITE;
/*!40000 ALTER TABLE `problem_tag` DISABLE KEYS */;
INSERT INTO `problem_tag` VALUES (1,1,2),(2,1,3),(3,3,1),(4,2,1),(5,2,2);
/*!40000 ALTER TABLE `problem_tag` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `solution`
--

DROP TABLE IF EXISTS `solution`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `solution` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `Id_Problem` int NOT NULL,
  `Tex` mediumtext COLLATE utf8mb4_general_ci NOT NULL,
  `Solver` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `Dep_Solu` tinyint NOT NULL,
  PRIMARY KEY (`Id`),
  KEY `FK_SOLUTION_PROBLEM_idx` (`Id_Problem`),
  CONSTRAINT `FK_SOLUTION_PROBLEM` FOREIGN KEY (`Id_Problem`) REFERENCES `problem` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `solution`
--

LOCK TABLES `solution` WRITE;
/*!40000 ALTER TABLE `solution` DISABLE KEYS */;
/*!40000 ALTER TABLE `solution` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tag`
--

DROP TABLE IF EXISTS `tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tag` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tag`
--

LOCK TABLES `tag` WRITE;
/*!40000 ALTER TABLE `tag` DISABLE KEYS */;
INSERT INTO `tag` VALUES (1,'analisis'),(2,'algebra'),(3,'tvm'),(4,'tcd'),(5,'integral');
/*!40000 ALTER TABLE `tag` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `Id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  `password` char(64) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`Id`),
  UNIQUE KEY `username_UNIQUE` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'almahill','6780304f9c37b51ab7e448f922dffcd3dc1889835b2cd26d0239f104d1e11d9f');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-04-16 12:52:40
