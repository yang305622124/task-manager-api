-- ----------------------------
-- Table structure for t_user_apps
-- ----------------------------
CREATE TABLE `t_user_apps` (
  `app_id` varchar(50) NOT NULL COMMENT '主键ID',
  `name` varchar(50) DEFAULT NULL COMMENT '渠道名称',
  `status` int DEFAULT '1' COMMENT '状态(0 冻结, 1 激活)',
  `del_flag` int DEFAULT '1' COMMENT '删除标志(0 删除, 1 存在)',
  `create_by` varchar(50) DEFAULT NULL COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(50) DEFAULT NULL COMMENT '修改者',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`app_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for t_user_users
-- ----------------------------
CREATE TABLE `t_user_users` (
  `user_id` varchar(50) NOT NULL COMMENT '主键ID',
  `app_id` varchar(50) DEFAULT NULL COMMENT '外键,渠道表ID',
  `username` varchar(50) DEFAULT NULL COMMENT '用户名',
  `password` varchar(50) DEFAULT NULL COMMENT '密码',
  `tel` varchar(50) DEFAULT NULL COMMENT '电话',
  `sex` int DEFAULT '1' COMMENT '性别(0 女, 1 男)',
  `status` int DEFAULT '1' COMMENT '状态(0 冻结, 1 激活)',
  `del_flag` int DEFAULT '1' COMMENT '删除标志(0 删除, 1 存在)',
  `create_by` varchar(50) DEFAULT NULL COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(50) DEFAULT NULL COMMENT '修改者',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;