-- ----------------------------
-- Table structure for task
-- ----------------------------
DROP TABLE IF EXISTS `task`;
CREATE TABLE `task` (
  `id` varchar(50) NOT NULL COMMENT '主键ID',
  `title` varchar(200) DEFAULT NULL COMMENT '任务标题',
  `description` varchar(500) DEFAULT NULL COMMENT '任务描述',
  `status` varchar(20) DEFAULT NULL COMMENT '状态(todo | in_progress | done)',
  `created_at` datetime DEFAULT NULL COMMENT '行创建时间',
  `updated_at` datetime DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

SET FOREIGN_KEY_CHECKS = 1;
