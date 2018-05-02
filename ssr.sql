/*
Navicat MySQL Data Transfer

Source Server         : 5$
Source Server Version : 50721
Source Host           : 198.13.43.118:3306
Source Database       : ssr

Target Server Type    : MYSQL
Target Server Version : 50721
File Encoding         : 65001

Date: 2018-05-01 12:02:49
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for orders
-- ----------------------------
DROP TABLE IF EXISTS `orders`;
CREATE TABLE `orders` (
  `id` varchar(60) COLLATE utf8_bin NOT NULL,
  `userId` varchar(60) COLLATE utf8_bin NOT NULL COMMENT '商品类别id',
  `password` varchar(60) COLLATE utf8_bin NOT NULL COMMENT '密码',
  `port` varchar(4) COLLATE utf8_bin NOT NULL COMMENT '端口号',
  `method` varchar(20) COLLATE utf8_bin NOT NULL COMMENT '加密类型',
  `protocol` varchar(30) COLLATE utf8_bin NOT NULL COMMENT '协议',
  `obfs` varchar(30) COLLATE utf8_bin NOT NULL COMMENT '混淆模式',
  `limit` varchar(30) COLLATE utf8_bin DEFAULT NULL,
  `used` varchar(30) COLLATE utf8_bin DEFAULT NULL,
  `total` varchar(30) COLLATE utf8_bin NOT NULL,
  `beginTm` datetime NOT NULL,
  `endTm` datetime NOT NULL,
  `createId` varchar(60) COLLATE utf8_bin NOT NULL COMMENT '创建者id',
  `updateId` varchar(60) COLLATE utf8_bin DEFAULT NULL,
  `createTm` datetime NOT NULL COMMENT '创建时间',
  `updateTm` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `index` (`id`,`port`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- ----------------------------
-- Records of orders
-- ----------------------------

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` varchar(60) COLLATE utf8_bin NOT NULL COMMENT '用户id',
  `userName` varchar(60) COLLATE utf8_bin NOT NULL COMMENT '用户名',
  `password` varchar(60) COLLATE utf8_bin NOT NULL,
  `email` varchar(60) COLLATE utf8_bin DEFAULT NULL COMMENT '邮箱',
  `sex` varchar(1) COLLATE utf8_bin DEFAULT NULL COMMENT '性别',
  `headUrl` varchar(200) COLLATE utf8_bin DEFAULT NULL COMMENT '头像url',
  `role` varchar(10) COLLATE utf8_bin NOT NULL COMMENT '0为管理员',
  `createId` varchar(60) COLLATE utf8_bin NOT NULL,
  `updateId` varchar(60) COLLATE utf8_bin DEFAULT NULL,
  `createTm` datetime NOT NULL COMMENT '创建时间',
  `updateTm` datetime DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`id`),
  KEY `index` (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES ('1', 'admin', 'e10adc3949ba59abbe56e057f20f883e', '874694517@qq.com', 'M', 'http://www.baidu.com', '0', '', null, '2018-04-14 19:53:31', '2018-04-14 19:53:38');
INSERT INTO `users` VALUES ('2', 'hms', 'e10adc3949ba59abbe56e057f20f883e', '874694511@qq.com', 'M', null, '0', '', null, '2018-04-17 21:09:38', '2018-04-17 21:09:41');
