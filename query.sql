-- MySQL dump 10.13  Distrib 8.0.45, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: pc
-- ------------------------------------------------------
-- Server version	8.0.45

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
-- Table structure for table `등급`
--

DROP TABLE IF EXISTS `등급`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `등급` (
  `등급_id` int NOT NULL AUTO_INCREMENT,
  `등급이름` varchar(50) NOT NULL,
  `할인율` decimal(5,2) NOT NULL,
  `최소포인트` int NOT NULL,
  PRIMARY KEY (`등급_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `등급`
--

LOCK TABLES `등급` WRITE;
/*!40000 ALTER TABLE `등급` DISABLE KEYS */;
INSERT INTO `등급` VALUES (1,'일반',0.00,0),(2,'실버',5.00,1000),(3,'골드',10.00,5000);
/*!40000 ALTER TABLE `등급` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `음식`
--

DROP TABLE IF EXISTS `음식`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `음식` (
  `음식_id` int NOT NULL AUTO_INCREMENT,
  `음식이름` varchar(100) NOT NULL,
  `가격` int NOT NULL,
  PRIMARY KEY (`음식_id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `음식`
--

LOCK TABLES `음식` WRITE;
/*!40000 ALTER TABLE `음식` DISABLE KEYS */;
INSERT INTO `음식` VALUES (1,'짜장라면',3500),(2,'김치볶음밥',6000),(3,'소떡소떡',4500),(4,'핫도그',3000),(5,'불닭마요덮밥',7500),(6,'아이스 아메리카노',2500),(7,'콜라 캔',1500);
/*!40000 ALTER TABLE `음식` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `음식주문_상세`
--

DROP TABLE IF EXISTS `음식주문_상세`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `음식주문_상세` (
  `주문상세_id` int NOT NULL AUTO_INCREMENT,
  `주문_id` int NOT NULL,
  `음식_id` int NOT NULL,
  `수량` int NOT NULL,
  `단가` int NOT NULL,
  `라인금액` int NOT NULL,
  PRIMARY KEY (`주문상세_id`),
  KEY `idx_order` (`주문_id`),
  KEY `idx_food` (`음식_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `음식주문_상세`
--

LOCK TABLES `음식주문_상세` WRITE;
/*!40000 ALTER TABLE `음식주문_상세` DISABLE KEYS */;
INSERT INTO `음식주문_상세` VALUES (1,1,1,2,3500,7000);
/*!40000 ALTER TABLE `음식주문_상세` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `음식주문_헤더`
--

DROP TABLE IF EXISTS `음식주문_헤더`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `음식주문_헤더` (
  `주문_id` int NOT NULL AUTO_INCREMENT,
  `회원_id` int NOT NULL,
  `주문일시` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `정가합계` int NOT NULL,
  `할인금액` int NOT NULL,
  `최종결제금액` int NOT NULL,
  PRIMARY KEY (`주문_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `음식주문_헤더`
--

LOCK TABLES `음식주문_헤더` WRITE;
/*!40000 ALTER TABLE `음식주문_헤더` DISABLE KEYS */;
INSERT INTO `음식주문_헤더` VALUES (1,2,'2026-01-29 15:08:16',7000,0,7000);
/*!40000 ALTER TABLE `음식주문_헤더` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `이용권`
--

DROP TABLE IF EXISTS `이용권`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `이용권` (
  `이용권_id` int NOT NULL AUTO_INCREMENT,
  `이용권명` varchar(50) NOT NULL,
  `가격` int NOT NULL,
  PRIMARY KEY (`이용권_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `이용권`
--

LOCK TABLES `이용권` WRITE;
/*!40000 ALTER TABLE `이용권` DISABLE KEYS */;
INSERT INTO `이용권` VALUES (1,'1시간 이용권',1200),(2,'3시간 이용권',3500),(3,'5시간 이용권',5000),(4,'10시간 이용권',9000),(5,'20시간 이용권',17000),(6,'종일권',20000);
/*!40000 ALTER TABLE `이용권` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `이용권구매내역`
--

DROP TABLE IF EXISTS `이용권구매내역`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `이용권구매내역` (
  `이용권구매_id` int NOT NULL AUTO_INCREMENT,
  `회원_id` int NOT NULL,
  `이용권_id` int NOT NULL,
  `최종결제금액` int DEFAULT NULL,
  `구매일시` datetime DEFAULT NULL,
  PRIMARY KEY (`이용권구매_id`),
  KEY `idx_tp_member_id` (`회원_id`),
  KEY `idx_tp_ticket_id` (`이용권_id`),
  CONSTRAINT `fk_tp_member` FOREIGN KEY (`회원_id`) REFERENCES `회원` (`회원_id`),
  CONSTRAINT `fk_tp_ticket` FOREIGN KEY (`이용권_id`) REFERENCES `이용권` (`이용권_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `이용권구매내역`
--

LOCK TABLES `이용권구매내역` WRITE;
/*!40000 ALTER TABLE `이용권구매내역` DISABLE KEYS */;
/*!40000 ALTER TABLE `이용권구매내역` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `장바구니`
--

DROP TABLE IF EXISTS `장바구니`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `장바구니` (
  `장바구니_id` int NOT NULL AUTO_INCREMENT,
  `회원_id` int NOT NULL,
  `음식_id` int NOT NULL,
  `수량` int NOT NULL DEFAULT '1',
  `담은일시` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`장바구니_id`),
  UNIQUE KEY `uk_member_food` (`회원_id`,`음식_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `장바구니`
--

LOCK TABLES `장바구니` WRITE;
/*!40000 ALTER TABLE `장바구니` DISABLE KEYS */;
/*!40000 ALTER TABLE `장바구니` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `주문접수`
--

DROP TABLE IF EXISTS `주문접수`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `주문접수` (
  `주문접수_id` int NOT NULL AUTO_INCREMENT,
  `주문유형` varchar(10) NOT NULL,
  `참조_id` int NOT NULL,
  `회원_id` int NOT NULL,
  `요청일시` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `상태` varchar(10) NOT NULL DEFAULT '대기',
  `처리일시` datetime DEFAULT NULL,
  `메모` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`주문접수_id`),
  KEY `idx_status_time` (`상태`,`요청일시`),
  KEY `idx_member` (`회원_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `주문접수`
--

LOCK TABLES `주문접수` WRITE;
/*!40000 ALTER TABLE `주문접수` DISABLE KEYS */;
INSERT INTO `주문접수` VALUES (1,'FOOD',1,2,'2026-01-29 15:08:16','대기',NULL,NULL);
/*!40000 ALTER TABLE `주문접수` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `패키지`
--

DROP TABLE IF EXISTS `패키지`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `패키지` (
  `패키지_id` int NOT NULL AUTO_INCREMENT,
  `패키지명` varchar(45) DEFAULT NULL,
  `연령대` int DEFAULT NULL,
  `가격` int NOT NULL,
  `음식_id` int NOT NULL,
  `이용권_id` int NOT NULL,
  PRIMARY KEY (`패키지_id`),
  KEY `fk_package_food1_idx` (`음식_id`),
  KEY `fk_package_ticket1_idx` (`이용권_id`),
  CONSTRAINT `fk_package_food1` FOREIGN KEY (`음식_id`) REFERENCES `음식` (`음식_id`),
  CONSTRAINT `fk_package_ticket1` FOREIGN KEY (`이용권_id`) REFERENCES `이용권` (`이용권_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `패키지`
--

LOCK TABLES `패키지` WRITE;
/*!40000 ALTER TABLE `패키지` DISABLE KEYS */;
INSERT INTO `패키지` VALUES (1,'10대 인기 패키지',10,11250,1,4),(2,'20대 인기 패키지',20,8550,2,2),(3,'30대 인기 패키지',30,7830,5,1),(4,'40대 인기 패키지',40,5850,7,3),(5,'50대 인기 패키지',50,7200,3,2);
/*!40000 ALTER TABLE `패키지` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `패키지구매`
--

DROP TABLE IF EXISTS `패키지구매`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `패키지구매` (
  `패키지구매_id` int NOT NULL AUTO_INCREMENT,
  `구매일시` datetime DEFAULT NULL,
  `회원_id` int NOT NULL,
  `패키지_id` int NOT NULL,
  `최종결제금액` int DEFAULT NULL,
  PRIMARY KEY (`패키지구매_id`),
  KEY `fk_packagepurchase_member1_idx` (`회원_id`),
  KEY `fk_packagepurchase_package1_idx` (`패키지_id`),
  CONSTRAINT `fk_packagepurchase_member1` FOREIGN KEY (`회원_id`) REFERENCES `회원` (`회원_id`),
  CONSTRAINT `fk_packagepurchase_package1` FOREIGN KEY (`패키지_id`) REFERENCES `패키지` (`패키지_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `패키지구매`
--

LOCK TABLES `패키지구매` WRITE;
/*!40000 ALTER TABLE `패키지구매` DISABLE KEYS */;
/*!40000 ALTER TABLE `패키지구매` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `포인트`
--

DROP TABLE IF EXISTS `포인트`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `포인트` (
  `포인트_id` int NOT NULL AUTO_INCREMENT,
  `회원_id` int NOT NULL,
  `유형` varchar(20) DEFAULT NULL,
  `포인트` int NOT NULL,
  `발생일시` datetime DEFAULT NULL,
  PRIMARY KEY (`포인트_id`),
  KEY `idx_ph_member_id` (`회원_id`),
  CONSTRAINT `fk_ph_member` FOREIGN KEY (`회원_id`) REFERENCES `회원` (`회원_id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `포인트`
--

LOCK TABLES `포인트` WRITE;
/*!40000 ALTER TABLE `포인트` DISABLE KEYS */;
INSERT INTO `포인트` VALUES (1,1,'적립',50,'2026-01-21 12:05:10'),(2,1,'적립',100,'2026-01-21 12:10:10'),(3,1,'적립',80,'2026-01-21 12:20:10'),(4,2,'적립',114,'2026-01-28 22:09:33'),(5,2,'적립',12,'2026-01-28 22:10:54'),(6,2,'적립',70,'2026-01-28 22:29:03'),(7,2,'적립',120,'2026-01-29 09:48:09'),(8,2,'적립',120,'2026-01-29 09:48:20'),(9,2,'적립',150,'2026-01-29 10:40:24'),(10,2,'적립',225,'2026-01-29 10:53:39'),(11,2,'적립',35,'2026-01-29 11:00:13'),(12,1,'적립',66,'2026-01-29 11:12:13'),(13,2,'적립',147,'2026-01-29 13:10:43'),(14,2,'적립',70,'2026-01-29 15:08:16');
/*!40000 ALTER TABLE `포인트` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `회원`
--

DROP TABLE IF EXISTS `회원`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `회원` (
  `회원_id` int NOT NULL AUTO_INCREMENT,
  `회원명` varchar(100) NOT NULL,
  `가입일시` datetime DEFAULT NULL,
  `연령대` int DEFAULT NULL,
  `등급_id` int DEFAULT NULL,
  PRIMARY KEY (`회원_id`),
  UNIQUE KEY `회원_id_UNIQUE` (`회원_id`),
  KEY `idx_member_grade_id` (`등급_id`),
  CONSTRAINT `fk_member_grade` FOREIGN KEY (`등급_id`) REFERENCES `등급` (`등급_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `회원`
--

LOCK TABLES `회원` WRITE;
/*!40000 ALTER TABLE `회원` DISABLE KEYS */;
INSERT INTO `회원` VALUES (1,'김예진','2026-01-10 10:00:00',30,1),(2,'문지하','2026-01-12 11:30:00',20,2),(3,'안선우','2026-01-15 09:10:00',40,3),(4,'김진수','2026-01-18 14:00:00',10,2),(5,'김지석','2026-01-20 16:20:00',50,1);
/*!40000 ALTER TABLE `회원` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-29 15:12:01
