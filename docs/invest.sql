-- MySQL dump 10.13  Distrib 8.0.22, for Linux (x86_64)
--
-- Host: localhost    Database: invest
-- ------------------------------------------------------
-- Server version	8.0.22

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `bias_22`
--

DROP TABLE IF EXISTS `bias_22`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bias_22` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `code` char(12) NOT NULL,
  `date` date NOT NULL,
  `bias` decimal(12,2) NOT NULL COMMENT '22 日 bias',
  PRIMARY KEY (`id`),
  KEY `code` (`code`,`date`)
) ENGINE=InnoDB AUTO_INCREMENT=33374 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `crawl_log`
--

DROP TABLE IF EXISTS `crawl_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `crawl_log` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `code` char(12) NOT NULL DEFAULT '' COMMENT '股票代码',
  `status` tinyint NOT NULL DEFAULT '0' COMMENT '爬取状态，0：成功，1：失败.',
  `message` varchar(255) NOT NULL DEFAULT '',
  `date` date NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=875 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `price_monitor`
--

DROP TABLE IF EXISTS `price_monitor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `price_monitor` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `code` char(12) NOT NULL,
  `buy_price` decimal(12,2) NOT NULL,
  `sell_price` decimal(12,2) NOT NULL,
  `message` text NOT NULL,
  `status` tinyint unsigned NOT NULL COMMENT '是否开启，0：关闭，1：开启',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '备注信息',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stock_day`
--

DROP TABLE IF EXISTS `stock_day`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stock_day` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` char(12) NOT NULL DEFAULT '' COMMENT '股票代码',
  `open` decimal(12,4) NOT NULL DEFAULT '0.0000' COMMENT '今天开盘价',
  `high` decimal(12,4) NOT NULL DEFAULT '0.0000' COMMENT '最高价',
  `low` decimal(12,4) NOT NULL DEFAULT '0.0000' COMMENT '最低价',
  `close` decimal(12,4) NOT NULL DEFAULT '0.0000' COMMENT '今天收盘价',
  `preclose` decimal(12,4) NOT NULL DEFAULT '0.0000' COMMENT '昨日收盘价',
  `volume` bigint NOT NULL DEFAULT '0' COMMENT '成交数量（单位：股）',
  `amount` decimal(16,4) NOT NULL DEFAULT '0.0000' COMMENT '成交金额',
  `turn` decimal(16,4) NOT NULL DEFAULT '0.0000' COMMENT '换手率',
  `pe_ttm` decimal(16,4) NOT NULL DEFAULT '0.0000' COMMENT '滚动市盈率',
  `date` date NOT NULL COMMENT '日期',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `index2` (`code`,`date`)
) ENGINE=InnoDB AUTO_INCREMENT=34166 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stocks`
--

DROP TABLE IF EXISTS `stocks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stocks` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `code` char(12) NOT NULL DEFAULT '' COMMENT '股票代码',
  `code_name` varchar(45) NOT NULL DEFAULT '' COMMENT '股票昵称',
  `is_init` tinyint NOT NULL DEFAULT '0' COMMENT '是否已初始化，0：否，1：已初始化',
  `init_date` date NOT NULL COMMENT '初始化历史数据，开始日期',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `status` tinyint NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-01-10  0:54:35
