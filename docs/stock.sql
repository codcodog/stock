-- MariaDB dump 10.17  Distrib 10.4.12-MariaDB, for Linux (x86_64)
--
-- Host: 172.17.0.2    Database: stock
-- ------------------------------------------------------
-- Server version	10.4.12-MariaDB-1:10.4.12+maria~bionic

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `crawl_log`
--

DROP TABLE IF EXISTS `crawl_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `crawl_log` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `code` char(12) NOT NULL DEFAULT '' COMMENT '股票代码',
  `status` tinyint(4) NOT NULL DEFAULT 0 COMMENT '爬取状态，0：成功，1：失败.',
  `message` varchar(255) NOT NULL DEFAULT '',
  `date` date NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stock_day`
--

DROP TABLE IF EXISTS `stock_day`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stock_day` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` char(12) NOT NULL DEFAULT '' COMMENT '股票代码',
  `open` decimal(12,4) NOT NULL DEFAULT 0.0000 COMMENT '今天开盘价',
  `high` decimal(12,4) NOT NULL DEFAULT 0.0000 COMMENT '最高价',
  `low` decimal(12,4) NOT NULL DEFAULT 0.0000 COMMENT '最低价',
  `close` decimal(12,4) NOT NULL DEFAULT 0.0000 COMMENT '今天收盘价',
  `preclose` decimal(12,4) NOT NULL DEFAULT 0.0000 COMMENT '昨日收盘价',
  `volume` bigint(20) NOT NULL DEFAULT 0 COMMENT '成交数量（单位：股）',
  `amount` decimal(16,4) NOT NULL DEFAULT 0.0000 COMMENT '成交金额',
  `date` date NOT NULL COMMENT '日期',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp() COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `stocks`
--

DROP TABLE IF EXISTS `stocks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stocks` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `code` char(12) NOT NULL DEFAULT '' COMMENT '股票代码',
  `code_name` varchar(45) NOT NULL DEFAULT '' COMMENT '股票昵称',
  `is_init` tinyint(4) NOT NULL DEFAULT 0 COMMENT '是否已初始化，0：否，1：已初始化',
  `init_date` date NOT NULL COMMENT '初始化历史数据，开始日期',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `status` tinyint(4) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-03-10 15:56:39
