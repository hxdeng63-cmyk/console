-- ============================================================
-- Flyway Versioned Migration: V5__seed_comprehensive
-- 综合种子数据填充 (基于gap分析补充)
-- 依赖: V1__init_schema, V2__init_data, V3__seed_comprehensive, V4__seed_video_and_stream
-- 说明: 补充更多真实业务数据，确保前后端联调有足够数据支撑
-- ============================================================

-- --------------------------------------------------------------
-- 1. 联动规则-设备关联补充数据 (linkage_rule_device)
-- 当前: 10条规则已关联部分设备，补充更多关联数据
-- --------------------------------------------------------------

-- 补充规则1(异常停车检测)关联更多设备
INSERT INTO linkage_rule_device (linkage_rule_id, device_id, created_at)
SELECT 1, id, NOW() FROM device WHERE id NOT IN (SELECT device_id FROM linkage_rule_device WHERE linkage_rule_id = 1) AND id <= 10;

-- 补充规则5(交通拥堵)关联西宁设备
INSERT INTO linkage_rule_device (linkage_rule_id, device_id, created_at)
SELECT 5, id, NOW() FROM device WHERE id IN (9, 10, 11, 12, 19, 20)
AND id NOT IN (SELECT device_id FROM linkage_rule_device WHERE linkage_rule_id = 5);

-- 补充规则6(烟雾火灾)关联养护设备
INSERT INTO linkage_rule_device (linkage_rule_id, device_id, created_at)
SELECT 6, id, NOW() FROM device WHERE id IN (7, 8)
AND id NOT IN (SELECT device_id FROM linkage_rule_device WHERE linkage_rule_id = 6);

-- --------------------------------------------------------------
-- 2. 部署-设备关联补充数据 (deployment_device)
-- 当前: 5个部署各关联部分设备
-- --------------------------------------------------------------

-- 部署1(海东道路监控)补充关联设备17,18
INSERT INTO deployment_device (deployment_id, device_id, created_at)
SELECT 1, id, NOW() FROM device WHERE id IN (17, 18)
AND id NOT IN (SELECT device_id FROM deployment_device WHERE deployment_id = 1);

-- 部署2(西宁高速监控)补充关联设备19,20
INSERT INTO deployment_device (deployment_id, device_id, created_at)
SELECT 2, id, NOW() FROM device WHERE id IN (19, 20)
AND id NOT IN (SELECT device_id FROM deployment_device WHERE deployment_id = 2);

-- 新增部署6: 格尔木进藏通道监控
INSERT INTO deployment (id, name, algorithm_id, service_id, status, algorithm_status, deployed_at, created_at, updated_at)
VALUES (6, '格尔木进藏通道监控', 11, 2, 'active', 'running', NOW() - INTERVAL '1 days', NOW(), NOW());

-- 部署6关联格尔木设备13,14
INSERT INTO deployment_device (deployment_id, device_id, created_at)
VALUES (6, 13, NOW()), (6, 14, NOW());

-- 新增部署7: 应急车道监控专项
INSERT INTO deployment (id, name, algorithm_id, service_id, status, algorithm_status, deployed_at, created_at, updated_at)
VALUES (7, '应急车道违规监控', 11, 1, 'active', 'running', NOW() - INTERVAL '6 hours', NOW(), NOW());

-- 部署7关联应急车道设备17,18
INSERT INTO deployment_device (deployment_id, device_id, created_at)
VALUES (7, 17, NOW()), (7, 18, NOW());

SELECT setval('deployment_id_seq', 7);

-- --------------------------------------------------------------
-- 3. 部署排期补充数据 (deployment_schedule)
-- --------------------------------------------------------------

-- 部署4(养护中心): 工作日 8:00-18:00
INSERT INTO deployment_schedule (deployment_id, day_of_week, start_time, end_time, created_at, updated_at)
VALUES
(4, 1, '08:00:00', '18:00:00', NOW(), NOW()),
(4, 2, '08:00:00', '18:00:00', NOW(), NOW()),
(4, 3, '08:00:00', '18:00:00', NOW(), NOW()),
(4, 4, '08:00:00', '18:00:00', NOW(), NOW()),
(4, 5, '08:00:00', '18:00:00', NOW(), NOW());

-- 部署5(车牌识别): 全天候
INSERT INTO deployment_schedule (deployment_id, day_of_week, start_time, end_time, created_at, updated_at)
SELECT 5, d, '00:00:00', '23:59:59', NOW(), NOW() FROM generate_series(0, 6) AS d;

-- 部署6(格尔木): 全天候
INSERT INTO deployment_schedule (deployment_id, day_of_week, start_time, end_time, created_at, updated_at)
SELECT 6, d, '00:00:00', '23:59:59', NOW(), NOW() FROM generate_series(0, 6) AS d;

-- 部署7(应急车道): 重点时段 6:00-22:00
INSERT INTO deployment_schedule (deployment_id, day_of_week, start_time, end_time, created_at, updated_at)
VALUES
(7, 0, '06:00:00', '22:00:00', NOW(), NOW()),
(7, 1, '06:00:00', '22:00:00', NOW(), NOW()),
(7, 2, '06:00:00', '22:00:00', NOW(), NOW()),
(7, 3, '06:00:00', '22:00:00', NOW(), NOW()),
(7, 4, '06:00:00', '22:00:00', NOW(), NOW()),
(7, 5, '06:00:00', '22:00:00', NOW(), NOW()),
(7, 6, '06:00:00', '22:00:00', NOW(), NOW());

-- --------------------------------------------------------------
-- 4. 任务-设备关联补充数据 (task_device)
-- --------------------------------------------------------------

-- 任务1补充设备15,16(备用设备)
INSERT INTO task_device (task_id, device_id, created_at)
SELECT 1, id, NOW() FROM device WHERE id IN (15, 16)
AND id NOT IN (SELECT device_id FROM task_device WHERE task_id = 1);

-- 新增任务6: 格尔木专项分析
INSERT INTO task (id, task_name, trigger_type, trigger_rule, algorithm_id, status, last_run_time, created_at, updated_at)
VALUES (6, '格尔木通道专项分析', 'cron', '0 0 */2 * * *', 11, 'active', NOW() - INTERVAL '2 hours', NOW(), NOW());

-- 任务6关联格尔木设备13,14
INSERT INTO task_device (task_id, device_id, created_at)
VALUES (6, 13, NOW()), (6, 14, NOW());

-- 新增任务7: 夜间巡检
INSERT INTO task (id, task_name, trigger_type, trigger_rule, algorithm_id, status, last_run_time, created_at, updated_at)
VALUES (7, '设备状态夜间巡检', 'cron', '0 0 2 * * *', 1, 'active', NOW() - INTERVAL '10 hours', NOW(), NOW());

-- 任务7关联主要设备1-14
INSERT INTO task_device (task_id, device_id, created_at)
SELECT 7, id, NOW() FROM device WHERE id <= 14;

SELECT setval('task_id_seq', 7);

-- --------------------------------------------------------------
-- 5. GB28181设备补充数据 (gb28181_device)
-- 当前: 5个GB28181设备，补充更多
-- --------------------------------------------------------------

-- 补充设备2,4,6的GB28181配置
INSERT INTO gb28181_device (id, device_id, manufacturer, model, sip_server_id, sip_device_id, status, channels_json, created_at, updated_at)
VALUES
(6, 2, '海康威视', 'DS-2CD3T86FWDV2-I3', '34020000002000000001', '34020000001320000002', 'active', '[{"channelId": "34020000001320000002", "name": "主码流"}, {"channelId": "34020000001320000002_s", "name": "子码流"}]'::jsonb, NOW(), NOW()),
(7, 4, '大华', 'DH-IPC-HFW8431E-Z', '34020000002000000002', '34020000001320000004', 'active', '[{"channelId": "34020000001320000004", "name": "主码流"}]'::jsonb, NOW(), NOW()),
(8, 6, '宇视科技', 'IPC2M4K', '34020000002000000003', '34020000001320000006', 'active', '[{"channelId": "34020000001320000006", "name": "主码流"}]'::jsonb, NOW(), NOW()),
(9, 13, '华为', 'M1221', '34020000002000000004', '34020000001320000013', 'active', '[{"channelId": "34020000001320000013", "name": "主码流"}]'::jsonb, NOW(), NOW()),
(10, 17, '海康威视', 'DS-2CD2T86FWDV2-I5', '34020000002000000005', '34020000001320000017', 'active', '[{"channelId": "34020000001320000017", "name": "主码流"}]'::jsonb, NOW(), NOW());

SELECT setval('gb28181_device_id_seq', 10);

-- --------------------------------------------------------------
-- 6. ONVIF设备补充数据 (onvif_device)
-- 当前: 5个ONVIF设备，补充更多
-- --------------------------------------------------------------

-- 补充更多设备的ONVIF配置
INSERT INTO onvif_device (id, device_id, manufacturer, model, ip, port, status, profiles_json, created_at, updated_at)
VALUES
(6, 1, 'Axis', 'P3225-LVE', '192.168.1.101'::inet, 80, 'active', '[{"token": "profile1", "name": "MainStream"}, {"token": "profile2", "name": "SubStream"}]'::jsonb, NOW(), NOW()),
(7, 7, 'Bosch', 'NIN-50022', '192.168.1.107'::inet, 80, 'active', '[{"token": "profile1", "name": "MainStream"}]'::jsonb, NOW(), NOW()),
(8, 8, 'Axis', 'P3245-VE', '192.168.1.108'::inet, 80, 'active', '[{"token": "profile1", "name": "MainStream"}]'::jsonb, NOW(), NOW()),
(9, 13, 'Sony', 'SNC-XM640', '192.168.1.113'::inet, 80, 'active', '[{"token": "profile1", "name": "MainStream"}]'::jsonb, NOW(), NOW()),
(10, 14, 'Panasonic', 'WV-S2131', '192.168.1.114'::inet, 80, 'active', '[{"token": "profile1", "name": "MainStream"}]'::jsonb, NOW(), NOW()),
(11, 15, 'Axis', 'P3225-LVE', '192.168.1.115'::inet, 80, 'inactive', '[{"token": "profile1", "name": "MainStream"}]'::jsonb, NOW(), NOW()),
(12, 17, 'Bosch', 'NIN-50022', '192.168.1.117'::inet, 80, 'active', '[{"token": "profile1", "name": "MainStream"}]'::jsonb, NOW(), NOW());

SELECT setval('onvif_device_id_seq', 12);

-- --------------------------------------------------------------
-- 7. 预置位补充数据 (preset)
-- 当前: 10个预置位，补充更多设备预置位
-- --------------------------------------------------------------

INSERT INTO preset (id, device_id, name, code, p, t, z, time_range_json, created_at, updated_at)
VALUES
(11, 2, '预置位1-主路', 'P01', 0.00, 0.00, 1.0, NULL, NOW(), NOW()),
(12, 2, '预置位2-应急车道', 'P02', 135.00, 10.00, 2.0, NULL, NOW(), NOW()),
(13, 4, '预置位1-主路', 'P01', 0.00, 0.00, 1.0, NULL, NOW(), NOW()),
(14, 4, '预置位2-应急车道', 'P02', 225.00, 15.00, 2.5, NULL, NOW(), NOW()),
(15, 6, '预置位1-入口', 'P01', 0.00, 0.00, 1.0, NULL, NOW(), NOW()),
(16, 6, '预置位2-出口', 'P02', 180.00, 0.00, 1.0, NULL, NOW(), NOW()),
(17, 7, '预置位1-全景', 'P01', 0.00, 0.00, 1.0, NULL, NOW(), NOW()),
(18, 7, '预置位2-入口', 'P02', 90.00, 20.00, 2.0, NULL, NOW(), NOW()),
(19, 8, '预置位1-全景', 'P01', 0.00, 0.00, 1.0, NULL, NOW(), NOW()),
(20, 8, '预置位2-出口', 'P02', 270.00, 15.00, 2.0, NULL, NOW(), NOW()),
(21, 10, '预置位1-主路', 'P01', 0.00, 0.00, 1.0, NULL, NOW(), NOW()),
(22, 10, '预置位2-路肩', 'P02', 45.00, 25.00, 2.5, NULL, NOW(), NOW()),
(23, 12, '预置位1-主路', 'P01', 0.00, 0.00, 1.0, NULL, NOW(), NOW()),
(24, 12, '预置位2-应急车道', 'P02', 315.00, 12.00, 2.0, NULL, NOW(), NOW()),
(25, 14, '预置位1-全景', 'P01', 0.00, 0.00, 1.0, NULL, NOW(), NOW()),
(26, 14, '预置位2-特写', 'P02', 60.00, 30.00, 3.0, NULL, NOW(), NOW()),
(27, 17, '预置位1-应急道', 'P01', 0.00, 0.00, 1.0, NULL, NOW(), NOW()),
(28, 17, '预置位2-主路', 'P02', 180.00, 10.00, 2.0, NULL, NOW(), NOW()),
(29, 18, '预置位1-应急道', 'P01', 0.00, 0.00, 1.0, NULL, NOW(), NOW()),
(30, 18, '预置位2-主路', 'P02', 0.00, 15.00, 2.0, NULL, NOW(), NOW());

SELECT setval('preset_id_seq', 30);

-- --------------------------------------------------------------
-- 8. 标注补充数据 (annotation)
-- 当前: 5个标注，补充更多设备标注
-- --------------------------------------------------------------

INSERT INTO annotation (id, deployment_id, device_id, name, type, polygon_json, color, created_at, updated_at)
VALUES
(6, 1, 3, '高速上行车道标注', 'monitoring', '[{"x":0.0,"y":0.3},{"x":1.0,"y":0.3},{"x":1.0,"y":0.7},{"x":0.0,"y":0.7}]'::jsonb, '#00FF00', NOW(), NOW()),
(7, 1, 4, '高速下行车道标注', 'monitoring', '[{"x":0.0,"y":0.3},{"x":1.0,"y":0.3},{"x":1.0,"y":0.7},{"x":0.0,"y":0.7}]'::jsonb, '#00FF00', NOW(), NOW()),
(8, 2, 9, '西宁道路标注', 'monitoring', '[{"x":0.05,"y":0.05},{"x":0.95,"y":0.05},{"x":0.95,"y":0.95},{"x":0.05,"y":0.95}]'::jsonb, '#00FF00', NOW(), NOW()),
(9, 2, 10, '西宁应急车道标注', 'forbidden', '[{"x":0.0,"y":0.0},{"x":0.2,"y":0.0},{"x":0.2,"y":1.0},{"x":0.0,"y":1.0}]'::jsonb, '#FF0000', NOW(), NOW()),
(10, 3, 6, '隧道出口标注', 'monitoring', '[{"x":0.2,"y":0.0},{"x":0.8,"y":0.0},{"x":0.8,"y":1.0},{"x":0.2,"y":1.0}]'::jsonb, '#00FF00', NOW(), NOW()),
(11, 6, 13, '进藏通道标注', 'monitoring', '[{"x":0.1,"y":0.2},{"x":0.9,"y":0.2},{"x":0.9,"y":0.8},{"x":0.1,"y":0.8}]'::jsonb, '#00FF00', NOW(), NOW()),
(12, 7, 17, '应急车道监测区', 'forbidden', '[{"x":0.0,"y":0.4},{"x":1.0,"y":0.4},{"x":1.0,"y":0.6},{"x":0.0,"y":0.6}]'::jsonb, '#FF0000', NOW(), NOW()),
(13, 7, 18, '应急车道监测区', 'forbidden', '[{"x":0.0,"y":0.4},{"x":1.0,"y":0.4},{"x":1.0,"y":0.6},{"x":0.0,"y":0.6}]'::jsonb, '#FF0000', NOW(), NOW()),
(14, 4, 8, '养护B区标注', 'monitoring', '[{"x":0.15,"y":0.15},{"x":0.85,"y":0.15},{"x":0.85,"y":0.85},{"x":0.15,"y":0.85}]'::jsonb, '#00FF00', NOW(), NOW()),
(15, 2, 11, '高速西宁上行车道', 'monitoring', '[{"x":0.0,"y":0.35},{"x":1.0,"y":0.35},{"x":1.0,"y":0.65},{"x":0.0,"y":0.65}]'::jsonb, '#00FF00', NOW(), NOW());

SELECT setval('annotation_id_seq', 15);

-- --------------------------------------------------------------
-- 9. 弹窗事件限制补充数据 (popup_event_limit)
-- 当前: 5个配置，补充更多设备
-- --------------------------------------------------------------

INSERT INTO popup_event_limit (id, device_id, time_interval_seconds, response_mode, enabled, created_at, updated_at)
VALUES
(6, 2, 45, 'immediate', true, NOW(), NOW()),
(7, 4, 30, 'immediate', true, NOW(), NOW()),
(8, 6, 15, 'immediate', true, NOW(), NOW()),
(9, 7, 60, 'delayed', true, NOW(), NOW()),
(10, 8, 60, 'delayed', true, NOW(), NOW()),
(11, 10, 20, 'immediate', true, NOW(), NOW()),
(12, 12, 25, 'immediate', true, NOW(), NOW()),
(13, 13, 30, 'immediate', true, NOW(), NOW()),
(14, 14, 30, 'immediate', true, NOW(), NOW()),
(15, 17, 15, 'immediate', true, NOW(), NOW()),
(16, 18, 15, 'immediate', true, NOW(), NOW());

SELECT setval('popup_event_limit_id_seq', 16);

-- --------------------------------------------------------------
-- 10. 清理记录补充数据 (clean_record)
-- 当前: 5条记录，补充更多
-- --------------------------------------------------------------

INSERT INTO clean_record (id, type, cutoff_time, status, progress, clean_size_bytes, created_at, updated_at, created_by)
VALUES
(6, '视频归档', NOW() - INTERVAL '60 days', 'completed', 100.00, 10737418240, NOW() - INTERVAL '10 days', NOW() - INTERVAL '10 days', 1),
(7, '日志清理', NOW() - INTERVAL '90 days', 'completed', 100.00, 2147483648, NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days', 1),
(8, '事件归档', NOW() - INTERVAL '30 days', 'running', 67.30, 3221225472, NOW(), NOW(), 1),
(9, '截图清理', NOW() - INTERVAL '7 days', 'pending', 0.00, 0, NOW(), NOW(), 1),
(10, '录像清理', NOW() - INTERVAL '180 days', 'pending', 0.00, 0, NOW(), NOW(), 1);

SELECT setval('clean_record_id_seq', 10);

-- --------------------------------------------------------------
-- 11. 操作日志补充数据 (operation_log)
-- 当前: 20条记录，补充更多
-- --------------------------------------------------------------

INSERT INTO operation_log (username, action, ip, result, module, action_time, created_at)
VALUES
('admin', '登录系统', '192.168.1.100'::inet, 'success', '认证', NOW() - INTERVAL '35 days', NOW() - INTERVAL '35 days'),
('admin', '查看设备列表', '192.168.1.100'::inet, 'success', '设备管理', NOW() - INTERVAL '34 days', NOW() - INTERVAL '34 days'),
('admin', '更新设备:S201-HD-002', '192.168.1.100'::inet, 'success', '设备管理', NOW() - INTERVAL '33 days', NOW() - INTERVAL '33 days'),
('admin', '创建联动规则:隧道监控', '192.168.1.100'::inet, 'success', '联动配置', NOW() - INTERVAL '32 days', NOW() - INTERVAL '32 days'),
('admin', '启用联动规则', '192.168.1.100'::inet, 'success', '联动配置', NOW() - INTERVAL '31 days', NOW() - INTERVAL '31 days'),
('operator', '登录系统', '192.168.1.101'::inet, 'success', '认证', NOW() - INTERVAL '30 days', NOW() - INTERVAL '30 days'),
('operator', '查看监控墙', '192.168.1.101'::inet, 'success', '视频监控', NOW() - INTERVAL '29 days', NOW() - INTERVAL '29 days'),
('operator', '查看推送历史', '192.168.1.101'::inet, 'success', '联动配置', NOW() - INTERVAL '28 days', NOW() - INTERVAL '28 days'),
('admin', '系统配置更新', '192.168.1.100'::inet, 'success', '系统配置', NOW() - INTERVAL '27 days', NOW() - INTERVAL '27 days'),
('admin', '查看算法服务', '192.168.1.100'::inet, 'success', '算法管理', NOW() - INTERVAL '26 days', NOW() - INTERVAL '26 days'),
('operator', '标注监控区域', '192.168.1.101'::inet, 'success', '算法管理', NOW() - INTERVAL '25 days', NOW() - INTERVAL '25 days'),
('operator', '查询事件记录', '192.168.1.101'::inet, 'success', '事件管理', NOW() - INTERVAL '24 days', NOW() - INTERVAL '24 days'),
('admin', '部署算法到设备', '192.168.1.100'::inet, 'success', '部署管理', NOW() - INTERVAL '23 days', NOW() - INTERVAL '23 days'),
('admin', '配置排期计划', '192.168.1.100'::inet, 'success', '部署管理', NOW() - INTERVAL '22 days', NOW() - INTERVAL '22 days'),
('operator', '登出系统', '192.168.1.101'::inet, 'success', '认证', NOW() - INTERVAL '21 days', NOW() - INTERVAL '21 days'),
('admin', 'GB28181平台同步', '192.168.1.100'::inet, 'success', '设备管理', NOW() - INTERVAL '19 days', NOW() - INTERVAL '19 days'),
('admin', 'ONVIF设备发现', '192.168.1.100'::inet, 'success', '设备管理', NOW() - INTERVAL '17 days', NOW() - INTERVAL '17 days'),
('admin', '创建设备分组', '192.168.1.100'::inet, 'success', '设备管理', NOW() - INTERVAL '15 days', NOW() - INTERVAL '15 days'),
('operator', '查看处置标签', '192.168.1.101'::inet, 'success', '系统配置', NOW() - INTERVAL '13 days', NOW() - INTERVAL '13 days'),
('operator', '查看弹窗设置', '192.168.1.101'::inet, 'success', '系统配置', NOW() - INTERVAL '11 days', NOW() - INTERVAL '11 days'),
('admin', '文件管理操作', '192.168.1.100'::inet, 'success', '文件管理', NOW() - INTERVAL '9 days', NOW() - INTERVAL '9 days'),
('admin', '固件升级操作', '192.168.1.100'::inet, 'success', '固件管理', NOW() - INTERVAL '7 days', NOW() - INTERVAL '7 days'),
('operator', '登录系统', '192.168.1.102'::inet, 'success', '认证', NOW() - INTERVAL '6 days', NOW() - INTERVAL '6 days'),
('operator', '查看算法服务列表', '192.168.1.102'::inet, 'success', '算法管理', NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days'),
('operator', '登出系统', '192.168.1.102'::inet, 'success', '认证', NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days'),
('admin', '批量导入设备', '192.168.1.100'::inet, 'success', '设备管理', NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days'),
('admin', '启动部署:海东道路', '192.168.1.100'::inet, 'success', '部署管理', NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days'),
('admin', '停止部署:车牌识别', '192.168.1.100'::inet, 'success', '部署管理', NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days'),
('operator', '实时预览监控', '192.168.1.101'::inet, 'success', '视频监控', NOW() - INTERVAL '1 days', NOW() - INTERVAL '1 days'),
('admin', '数据清理任务', '192.168.1.100'::inet, 'success', '系统配置', NOW() - INTERVAL '12 hours', NOW() - INTERVAL '12 hours');

-- --------------------------------------------------------------
-- 12. 推送历史补充数据 (push_history)
-- --------------------------------------------------------------

INSERT INTO push_history (id, rule_id, device_id, event_type_id, push_channels, push_target, push_time, status, retry_count, operator, count, detail, created_at)
VALUES
(16, 1, 2, 2, '["web","sms"]'::jsonb, '18600000001', NOW() - INTERVAL '1 days', 'success', 0, 'system', 2, '异常停车', NOW() - INTERVAL '1 days'),
(17, 2, 12, 3, '["web","sms","email"]'::jsonb, '18600000002', NOW() - INTERVAL '1 days', 'success', 0, 'system', 1, '逆向行驶', NOW() - INTERVAL '1 days'),
(18, 3, 10, 4, '["web"]'::jsonb, '18600000003', NOW() - INTERVAL '22 hours', 'success', 0, 'system', 1, '行人闯入', NOW() - INTERVAL '22 hours'),
(19, 4, 18, 5, '["web","sms"]'::jsonb, '18600000004', NOW() - INTERVAL '20 hours', 'success', 0, 'system', 1, '应急车道占用', NOW() - INTERVAL '20 hours'),
(20, 5, 14, 6, '["web"]'::jsonb, '18600000005', NOW() - INTERVAL '18 hours', 'success', 0, 'system', 4, '交通拥堵', NOW() - INTERVAL '18 hours'),
(21, 6, 7, 8, '["web","sms","email"]'::jsonb, '18600000006', NOW() - INTERVAL '15 hours', 'failed', 1, 'system', 1, '烟雾检测', NOW() - INTERVAL '15 hours'),
(22, 7, 8, 12, '["web"]'::jsonb, '18600000007', NOW() - INTERVAL '12 hours', 'success', 0, 'system', 1, '区域拥挤', NOW() - INTERVAL '12 hours'),
(23, 8, 13, 14, '["web","sms"]'::jsonb, '18600000008', NOW() - INTERVAL '10 hours', 'success', 0, 'system', 1, '越界检测', NOW() - INTERVAL '10 hours'),
(24, 9, 20, 15, '["web"]'::jsonb, '18600000009', NOW() - INTERVAL '8 hours', 'success', 0, 'system', 2, '人员聚集', NOW() - INTERVAL '8 hours'),
(25, 10, 3, 1, '["web"]'::jsonb, NULL, NOW() - INTERVAL '6 hours', 'success', 0, 'system', 8, '车牌识别', NOW() - INTERVAL '6 hours'),
(26, 1, 17, 2, '["web","sms"]'::jsonb, '18600000001', NOW() - INTERVAL '4 hours', 'success', 0, 'system', 1, '异常停车', NOW() - INTERVAL '4 hours'),
(27, 5, 19, 6, '["web"]'::jsonb, '18600000005', NOW() - INTERVAL '3 hours', 'success', 0, 'system', 2, '交通拥堵', NOW() - INTERVAL '3 hours'),
(28, 2, 4, 3, '["web","sms","email"]'::jsonb, '18600000002', NOW() - INTERVAL '2 hours', 'failed', 3, 'system', 1, '逆向行驶', NOW() - INTERVAL '2 hours'),
(29, 4, 17, 5, '["web","sms"]'::jsonb, '18600000004', NOW() - INTERVAL '1 hours', 'success', 0, 'system', 1, '应急车道占用', NOW() - INTERVAL '1 hours'),
(30, 6, 6, 8, '["web","sms","email"]'::jsonb, '18600000006', NOW() - INTERVAL '30 minutes', 'success', 0, 'system', 1, '烟雾检测', NOW() - INTERVAL '30 minutes');

SELECT setval('push_history_id_seq', 30);

-- --------------------------------------------------------------
-- 13. 接入平台补充数据 (access_platform)
-- --------------------------------------------------------------

INSERT INTO access_platform (id, name, type, version, device_count, status, config_json, created_at, updated_at)
VALUES
(2, '海东GB28181平台', 'GB28181', 'GB28181平台V2.0', 0, 'active', '{"domain": "3402000000", "realm": "3402000000"}'::jsonb, NOW(), NOW()),
(3, '西宁GB28181平台', 'GB28181', 'GB28181平台V1.5', 0, 'active', '{"domain": "3402000001", "realm": "3402000001"}'::jsonb, NOW(), NOW()),
(4, '格尔木GB28181平台', 'GB28181', 'GB28181平台V2.1', 0, 'active', '{"domain": "3402000002", "realm": "3402000002"}'::jsonb, NOW(), NOW()),
(5, 'Axis ONVIF平台', 'ONVIF', 'ONVIF Profile S', 0, 'active', '{"username": "admin", "password": "axis123"}'::jsonb, NOW(), NOW()),
(6, 'Bosch ONVIF平台', 'ONVIF', 'ONVIF Profile G', 0, 'active', '{"username": "admin", "password": "bosch456"}'::jsonb, NOW(), NOW());

SELECT setval('access_platform_id_seq', 6);

-- --------------------------------------------------------------
-- 完成提示
-- --------------------------------------------------------------
DO $$
BEGIN
    RAISE NOTICE 'V5__seed_comprehensive.sql executed successfully';
    RAISE NOTICE '补充数据包括:';
    RAISE NOTICE '  - 联动规则-设备关联补充';
    RAISE NOTICE '  - 新增部署6(格尔木)、部署7(应急车道)';
    RAISE NOTICE '  - 部署排期补充';
    RAISE NOTICE '  - 新增任务6(格尔木专项)、任务7(夜间巡检)';
    RAISE NOTICE '  - GB28181设备补充至10个';
    RAISE NOTICE '  - ONVIF设备补充至12个';
    RAISE NOTICE '  - 预置位补充至30个';
    RAISE NOTICE '  - 标注补充至15个';
    RAISE NOTICE '  - 弹窗事件限制补充至16个';
    RAISE NOTICE '  - 清理记录补充至10个';
    RAISE NOTICE '  - 操作日志补充至50条';
    RAISE NOTICE '  - 推送历史补充至30条';
    RAISE NOTICE '  - 接入平台补充至6个';
END $$;
