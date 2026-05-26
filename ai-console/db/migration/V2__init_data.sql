-- ============================================================
-- Flyway Versioned Migration: V2__init_data
-- 系统内置数据初始化
-- 依赖: V1__init_schema
-- 原则: 此文件只插入"系统启动必需"的数据；业务 Mock 数据使用后续迁移或外部脚本
-- ============================================================

-- --------------------------------------------------------------
-- 1. 超级管理员
-- --------------------------------------------------------------
INSERT INTO "user" (id, username, real_name, password, phone, email, gender, status, created_at, updated_at)
VALUES (1, 'admin', '系统管理员', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjXAgdZnJ3jN2BP5IaOU.ET8uLr0u2G', '18688888888', '', '', 'active', NOW(), NOW());

-- --------------------------------------------------------------
-- 2. 根组织
-- --------------------------------------------------------------
INSERT INTO organization (id, name, parent_id, level, sort, code, remark, created_at, updated_at)
VALUES (1, '青海省交通厅', NULL, 1, 1, 'ROOT', '根组织', NOW(), NOW());

-- --------------------------------------------------------------
-- 3. 超级管理员角色
-- --------------------------------------------------------------
INSERT INTO role (id, name, code, description, status, created_at, updated_at)
VALUES (1, '系统管理员', 'SUPER_ADMIN', '超级管理员，拥有全部权限', 'active', NOW(), NOW());

-- --------------------------------------------------------------
-- 4. 用户-角色绑定
-- --------------------------------------------------------------
INSERT INTO user_role (user_id, role_id, created_at) VALUES (1, 1, NOW());

-- --------------------------------------------------------------
-- 5. 接入协议平台
-- --------------------------------------------------------------
INSERT INTO access_platform (name, type, version, status, config_json, created_at, updated_at)
VALUES
('默认GB28181平台', 'GB28181', 'GB/T 28181-2016', 'active', '{"sipServer": "192.168.1.200", "sipPort": 5060}'::jsonb, NOW(), NOW()),
('默认ONVIF平台', 'ONVIF', 'Profile S/G', 'active', '{"discoveryTimeout": 5000}'::jsonb, NOW(), NOW()),
('默认RTSP平台', 'RTSP', 'RTSP/1.0', 'active', '{}'::jsonb, NOW(), NOW());

-- --------------------------------------------------------------
-- 6. UI 主题
-- --------------------------------------------------------------
INSERT INTO ui_theme (name, platform, theme_color, logo_url, is_active, created_at, updated_at)
VALUES ('默认深色主题', 'web', '#00E5FF', '/logo.png', true, NOW(), NOW());

-- --------------------------------------------------------------
-- 7. 弹窗配置
-- --------------------------------------------------------------
INSERT INTO popup_setting (config_json, is_active, created_at, updated_at)
VALUES ('{"defaultTimeout": 5, "maxConcurrent": 10}'::jsonb, true, NOW(), NOW());

-- --------------------------------------------------------------
-- 8. 算法框架（16 种核心算法）
-- --------------------------------------------------------------
INSERT INTO algorithm (id, name, type, description, business_category, created_at, updated_at)
VALUES
(1, '视频抽帧', 'preprocess', '定时抽帧供后端分析', '通用', NOW(), NOW()),
(2, '人脸检测', 'detection', '检测画面中人脸位置', '通用安防', NOW(), NOW()),
(3, '车牌识别', 'detection', '识别车辆车牌号码', '交通场景', NOW(), NOW()),
(4, '行为分析', 'detection', '检测异常行为', '通用安防', NOW(), NOW()),
(5, '夜间分析', 'detection', '低照度场景增强分析', '通用安防', NOW(), NOW()),
(6, '拥挤检测', 'count', '检测区域人群密度', '通用安防', NOW(), NOW()),
(7, '遗留物检测', 'detection', '检测遗留物品', '通用安防', NOW(), NOW()),
(8, '越界检测', 'detection', '检测越界闯入行为', '通用安防', NOW(), NOW()),
(9, '周界防范', 'detection', '电子围栏入侵检测', '通用安防', NOW(), NOW()),
(10, '人员聚集', 'count', '统计聚集人数', '通用安防', NOW(), NOW()),
(11, '交通检测', 'traffic', '交通事件综合检测', '交通场景', NOW(), NOW()),
(12, '火灾检测', 'detection', '火焰/烟雾检测', '消防场景', NOW(), NOW()),
(13, '违章检测', 'traffic', '交通违章行为识别', '交通场景', NOW(), NOW()),
(14, '烟雾检测', 'detection', '烟雾识别', '消防场景', NOW(), NOW()),
(15, '区域拥挤', 'count', '区域人数超限', '通用安防', NOW(), NOW()),
(16, '行为异常', 'detection', '异常动作识别', '通用安防', NOW(), NOW());

SELECT setval('algorithm_id_seq', 16);

-- --------------------------------------------------------------
-- 9. 事件类型框架（基于算法生成的基础事件类型）
-- --------------------------------------------------------------
INSERT INTO event_type (algorithm_id, name, description, category, severity, created_at, updated_at)
VALUES
(3, '车牌识别', '识别到车辆车牌', 'detection', 2, NOW(), NOW()),
(11, '异常停车', '道路异常停车检测', 'traffic', 3, NOW(), NOW()),
(11, '逆向行驶', '车辆逆行检测', 'traffic', 4, NOW(), NOW()),
(11, '行人闯入', '行人进入机动车道', 'traffic', 3, NOW(), NOW()),
(11, '占用应急车道', '违规占用应急车道', 'traffic', 3, NOW(), NOW()),
(11, '交通阻塞', '道路拥堵检测', 'traffic', 3, NOW(), NOW()),
(11, '非机动车驶入', '非机动车进入禁行区域', 'traffic', 2, NOW(), NOW()),
(12, '烟雾', '检测到烟雾', 'detection', 5, NOW(), NOW()),
(11, '疑似事故', '疑似交通事故', 'traffic', 5, NOW(), NOW()),
(11, '作业人员', '检测到道路作业人员', 'traffic', 2, NOW(), NOW()),
(11, '作业车辆识别', '检测到道路作业车辆', 'traffic', 2, NOW(), NOW()),
(6, '区域拥挤', '区域人群密度超限', 'count', 3, NOW(), NOW()),
(2, '人脸识别', '检测到人脸', 'detection', 2, NOW(), NOW()),
(8, '越界检测', '越界闯入', 'detection', 3, NOW(), NOW()),
(10, '人员聚集', '人员聚集检测', 'count', 3, NOW(), NOW());

-- --------------------------------------------------------------
-- 10. 区域框架（示例：青海省交通路段）
-- --------------------------------------------------------------
INSERT INTO region (id, name, code, parent_id, level, sort, created_at, updated_at)
VALUES
(1, '青海省', 'QH', NULL, 1, 1, NOW(), NOW()),
(2, '海东市', 'QH-HD', 1, 2, 1, NOW(), NOW()),
(3, '西宁市', 'QH-XN', 1, 2, 2, NOW(), NOW()),
(4, '格尔木市', 'QH-GEM', 1, 2, 3, NOW(), NOW()),
(5, 'S201', 'QH-HD-S201', 2, 3, 1, NOW(), NOW()),
(6, 'G213', 'QH-HD-G213', 2, 3, 2, NOW(), NOW()),
(7, 'S201', 'QH-XN-S201', 3, 3, 1, NOW(), NOW()),
(8, 'G213', 'QH-XN-G213', 3, 3, 2, NOW(), NOW());

-- --------------------------------------------------------------
-- 11. 组织框架（分公司/养护中心）
-- --------------------------------------------------------------
INSERT INTO organization (id, name, parent_id, level, sort, code, remark, created_at, updated_at)
VALUES
(2, '海东分公司', 1, 2, 1, 'HD-FGS', '海东地区分公司', NOW(), NOW()),
(3, '西宁分公司', 1, 2, 2, 'XN-FGS', '西宁地区分公司', NOW(), NOW()),
(4, '养护中心A', 2, 3, 1, 'HD-YH-A', '海东养护中心A', NOW(), NOW()),
(5, '隧道管理所', 2, 3, 2, 'HD-SD', '海东隧道管理所', NOW(), NOW());

-- --------------------------------------------------------------
-- 12. 序列重置
-- --------------------------------------------------------------
SELECT setval('region_id_seq', 8);
SELECT setval('organization_id_seq', 5);
