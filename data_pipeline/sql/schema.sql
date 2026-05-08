-- 1. 如果不存在则创建数据库
CREATE DATABASE IF NOT EXISTS `ballinsight` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. 选中该数据库
USE `ballinsight`;

-- 3.1. 创建足球新闻基础表
CREATE TABLE IF NOT EXISTS `sys_news` (
  `id` varchar(64) NOT NULL COMMENT '新闻唯一ID',
  `title` varchar(255) NOT NULL COMMENT '新闻标题',
  `content` text NOT NULL COMMENT '新闻正文',
  `publish_time` datetime NOT NULL COMMENT '发布时间',
  `source` varchar(50) DEFAULT '懂球帝' COMMENT '来源',
  `sentiment_score` float DEFAULT NULL COMMENT '情感极性得分 (0-1) [创新点]',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3.2. 球队基础表 (sys_team)
CREATE TABLE IF NOT EXISTS `sys_team` (
  `team_id` int NOT NULL AUTO_INCREMENT COMMENT '球队ID',
  `team_name` varchar(100) NOT NULL COMMENT '球队全称',
  `league` varchar(50) DEFAULT NULL COMMENT '所属联赛',
  PRIMARY KEY (`team_id`),
  UNIQUE KEY `uk_team_name` (`team_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='球队数据表';

-- 3. 球员基础表 (sys_player) - 包含雷达图所需的核心六维数据
CREATE TABLE IF NOT EXISTS `sys_player` (
  `player_id` int NOT NULL AUTO_INCREMENT COMMENT '球员ID',
  `name` varchar(100) NOT NULL COMMENT '球员姓名',
  `team_name` varchar(100) DEFAULT NULL COMMENT '效力球队',
  `nationality` varchar(50) DEFAULT NULL COMMENT '国籍',
  `market_value` varchar(20) DEFAULT NULL COMMENT '身价 (如 €50.00m)',
  `overall_rating` int DEFAULT 0 COMMENT '综合能力值 (0-100)',
  -- 下面这 6 个字段是完美契合前端 Echarts 雷达图的素材
  `pace` int DEFAULT 0 COMMENT '速度',
  `shooting` int DEFAULT 0 COMMENT '射门',
  `passing` int DEFAULT 0 COMMENT '传球',
  `dribbling` int DEFAULT 0 COMMENT '盘带',
  `defending` int DEFAULT 0 COMMENT '防守',
  `physical` int DEFAULT 0 COMMENT '体能/力量',
  PRIMARY KEY (`player_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='球员数据表';