-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: localhost    Database: shuiyuan
-- ------------------------------------------------------
-- Server version	8.0.40-0ubuntu0.22.04.1

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
-- Table structure for table `Topic`
--

DROP TABLE IF EXISTS `Topic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Topic` (
  `id` int unsigned NOT NULL,
  `title` varchar(300) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `last_posted_at` datetime DEFAULT NULL,
  `posts_count` int unsigned DEFAULT NULL,
  `reply_count` int unsigned DEFAULT NULL,
  `views` int unsigned DEFAULT NULL,
  `like_count` int unsigned DEFAULT NULL,
  `has_accepted_answer` tinyint(1) DEFAULT NULL,
  `pinned` tinyint(1) DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `tags` varchar(100) DEFAULT NULL,
  `update_timestamp` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `Topic_User_FK` (`created_by`),
  CONSTRAINT `Topic_User_FK` FOREIGN KEY (`created_by`) REFERENCES `User` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `User`
--

DROP TABLE IF EXISTS `User`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `User` (
  `id` int NOT NULL,
  `username` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `trust_level` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'shuiyuan'
--
/*!50003 DROP PROCEDURE IF EXISTS `ADDTOPIC` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `ADDTOPIC`(
 IN Topic_id  int unsigned ,
 IN Topic_title  varchar(300) ,
 IN Topic_created_at  datetime ,
 IN Topic_last_posted_at  datetime ,
 IN Topic_posts_count  int unsigned ,
 IN Topic_reply_count  int unsigned ,
 IN Topic_views  int unsigned ,
 IN Topic_like_count  int unsigned,
 IN Topic_has_accepted_answer  tinyint(1) ,
 IN Topic_pinned  tinyint(1) ,
 IN Topic_created_by  int ,
 IN Topic_tags  varchar(100) ,
 IN Topic_update_timestamp  datetime 
)
BEGIN
	DECLARE topic_recordExists INT;
    -- 检查是否存在相同的ID
    SELECT COUNT(*) INTO topic_recordExists
    FROM Topic
    WHERE id = Topic_id;
    IF topic_recordExists > 0 THEN
        -- 如果存在，则更新记录
        UPDATE Topic
        SET 
        	title=Topic_title,
        	created_at=Topic_created_at,
        	last_posted_at=Topic_last_posted_at,
        	posts_count=Topic_posts_count,
        	reply_count=Topic_reply_count,
        	views=Topic_views,
        	like_count=Topic_like_count,
        	has_accepted_answer=Topic_has_accepted_answer,
        	pinned=Topic_pinned,
        	created_by=Topic_created_by,
        	tags=Topic_tags,
        	update_timestamp=Topic_update_timestamp
        WHERE id = Topic_id;
    ELSE
        -- 如果不存在，则插入新记录
        INSERT INTO shuiyuan.Topic
		(id, title, created_at, last_posted_at, posts_count, reply_count, views, like_count, has_accepted_answer, pinned, created_by, tags, update_timestamp)
		VALUES(Topic_id, Topic_title, Topic_created_at, Topic_last_posted_at, Topic_posts_count, Topic_reply_count, Topic_views, Topic_like_count, Topic_has_accepted_answer, Topic_pinned, Topic_created_by, Topic_tags, Topic_update_timestamp);
    END IF;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `ADDUSER` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `ADDUSER`(
	IN userId INT,         -- 用户ID
	IN userUserName VARCHAR(100), -- 用户昵称
    IN userName VARCHAR(100), -- 用户名
    IN userTrust_Level INT      -- 用户等级
    
)
BEGIN
    DECLARE recordExists INT;

    -- 检查是否存在相同的ID
    SELECT COUNT(*) INTO recordExists
    FROM User
    WHERE id = userId;

    IF recordExists > 0 THEN
        -- 如果存在，则更新记录
        UPDATE User
        SET name = userName,
            trust_level = userTrust_Level,
            username = userUserName
        WHERE id = userId;
    ELSE
        -- 如果不存在，则插入新记录
        INSERT INTO User (id, username, name, trust_level)
        VALUES (userId, userUserName, userName, userTrust_Level);
    END IF;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-12-14 19:59:49
