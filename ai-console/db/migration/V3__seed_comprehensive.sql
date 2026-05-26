-- ============================================================
-- Flyway Versioned Migration: V3__seed_comprehensive
-- 综合种子数据填充
-- 依赖: V1__init_schema, V2__init_data
-- 说明: 仅填充空表，已有的数据(user/organization/algorithm/event_type/access_platform/ui_theme/popup_setting/region)不受影响
-- ============================================================

-- --------------------------------------------------------------
-- 1. 角色 (已有SUPER_ADMIN=1，新增2个)
-- --------------------------------------------------------------
INSERT INTO role (id, name, code, description, status, created_at, updated_at)
VALUES
(2, '操作员', 'OPERATOR', '普通操作员，可操作设备与查看事件', 'active', NOW(), NOW()),
(3, '访客', 'GUEST', '访客账号，只读权限', 'active', NOW(), NOW());

SELECT setval('role_id_seq', 3);

-- --------------------------------------------------------------
-- 2. 菜单 (系统主菜单)
-- --------------------------------------------------------------
INSERT INTO menu (id, name, path, hidden, parent_id, sort, component, title, icon, created_at, updated_at)
VALUES
-- 一级菜单
(1, 'Dashboard', '/dashboard', false, NULL, 1, 'LAYOUT', '仪表盘', 'Odometer', NOW(), NOW()),
(2, '设备管理', '/device', false, NULL, 2, NULL, '设备管理', 'VideoCamera', NOW(), NOW()),
(3, '视频监控', '/monitor', false, NULL, 3, NULL, '视频监控', 'Monitor', NOW(), NOW()),
(4, '算法管理', '/algorithm', false, NULL, 4, NULL, '算法管理', 'Cpu', NOW(), NOW()),
(5, '联动配置', '/linkage', false, NULL, 5, NULL, '联动配置', 'Connection', NOW(), NOW()),
(6, '系统配置', '/system', false, NULL, 6, NULL, '系统配置', 'Setting', NOW(), NOW()),
-- Dashboard子菜单
(11, '首页概览', '/dashboard/home', false, 1, 1, '/views/dashboard/Home.vue', '首页概览', NULL, NOW(), NOW()),
-- 设备管理子菜单
(21, '设备列表', '/device/list', false, 2, 1, '/views/device/DeviceList.vue', '设备列表', NULL, NOW(), NOW()),
(22, '设备分组', '/device/group', false, 2, 2, '/views/device/DeviceGroup.vue', '设备分组', NULL, NOW(), NOW()),
(23, '区域管理', '/device/region', false, 2, 3, '/views/device/Region.vue', '区域管理', NULL, NOW(), NOW()),
(24, 'GB28181接入', '/device/gb28181', false, 2, 4, '/views/device/access/Gb28181.vue', 'GB28181接入', NULL, NOW(), NOW()),
(25, 'ONVIF接入', '/device/onvif', false, 2, 5, '/views/device/access/Onvif.vue', 'ONVIF接入', NULL, NOW(), NOW()),
(26, '平台列表', '/device/platform', false, 2, 6, '/views/device/access/PlatformList.vue', '平台列表', NULL, NOW(), NOW()),
-- 视频监控子菜单
(31, '监控墙', '/monitor/wall', false, 3, 1, '/views/monitor/MonitorWall.vue', '监控墙', NULL, NOW(), NOW()),
(32, '实时预览', '/monitor/preview', false, 3, 2, '/views/monitor/Preview.vue', '实时预览', NULL, NOW(), NOW()),
-- 算法管理子菜单
(41, '算法服务', '/algorithm/service', false, 4, 1, '/views/algorithm/AlgorithmService.vue', '算法服务', NULL, NOW(), NOW()),
(42, '事件类型', '/algorithm/event', false, 4, 2, '/views/algorithm/EventType.vue', '事件类型', NULL, NOW(), NOW()),
(43, '标注管理', '/algorithm/annotation', false, 4, 3, '/views/deployment/Annotation.vue', '标注管理', NULL, NOW(), NOW()),
-- 联动配置子菜单
(51, '联动规则', '/linkage/rule', false, 5, 1, '/views/linkage/LinkageRule.vue', '联动规则', NULL, NOW(), NOW()),
(52, '推送历史', '/linkage/push', false, 5, 2, '/views/linkage/PushHistory.vue', '推送历史', NULL, NOW(), NOW()),
(53, '任务管理', '/linkage/task', false, 5, 3, '/views/linkage/Task.vue', '任务管理', NULL, NOW(), NOW()),
-- 系统配置子菜单
(61, '录像配置', '/system/video', false, 6, 1, '/views/system/VideoSetting.vue', '录像配置', NULL, NOW(), NOW()),
(62, '文件管理', '/system/file', false, 6, 2, '/views/system/FileManager.vue', '文件管理', NULL, NOW(), NOW()),
(63, '弹窗设置', '/system/popup', false, 6, 3, '/views/system/PopupSetting.vue', '弹窗设置', NULL, NOW(), NOW()),
(64, '处置标签', '/system/dispose', false, 6, 4, '/views/system/DisposeTag.vue', '处置标签', NULL, NOW(), NOW()),
(65, '帮助中心', '/system/help', false, 6, 5, '/views/system/HelpCenter.vue', '帮助中心', NULL, NOW(), NOW()),
-- 高级管理员菜单
(101, '菜单管理', '/super-admin/menu', false, NULL, 99, '/views/super-admin/MenuManage.vue', '菜单管理', NULL, NOW(), NOW()),
(102, '资源权限', '/super-admin/resource', false, NULL, 99, '/views/super-admin/Resource.vue', '资源权限', NULL, NOW(), NOW()),
(103, '用户管理', '/super-admin/user', false, NULL, 99, '/views/super-admin/User.vue', '用户管理', NULL, NOW(), NOW()),
(104, '角色管理', '/super-admin/role', false, NULL, 99, '/views/super-admin/Role.vue', '角色管理', NULL, NOW(), NOW()),
(105, '组织架构', '/super-admin/org', false, NULL, 99, '/views/super-admin/Organization.vue', '组织架构', NULL, NOW(), NOW()),
(106, '操作日志', '/super-admin/log', false, NULL, 99, '/views/super-admin/OperationLog.vue', '操作日志', NULL, NOW(), NOW()),
(107, '固件管理', '/super-admin/firmware', false, NULL, 99, '/views/super-admin/Firmware.vue', '固件管理', NULL, NOW(), NOW()),
(108, 'License', '/super-admin/license', false, NULL, 99, '/views/super-admin/LicenseFile.vue', 'License', NULL, NOW(), NOW());

SELECT setval('menu_id_seq', 108);

-- --------------------------------------------------------------
-- 3. 角色-菜单绑定 (role_menu)
-- --------------------------------------------------------------
-- 管理员(SUPER_ADMIN=1)拥有所有菜单
INSERT INTO role_menu (role_id, menu_id, created_at)
SELECT 1, id, NOW() FROM menu;

-- 操作员(OPERATOR=2)拥有业务菜单(1-65)，不含超级管理后台
INSERT INTO role_menu (role_id, menu_id, created_at)
SELECT 2, id, NOW() FROM menu WHERE id <= 65;

-- 访客(GUEST=3)仅拥有首页概览和监控墙
INSERT INTO role_menu (role_id, menu_id, created_at)
SELECT 3, id, NOW() FROM menu WHERE id IN (11, 31);

-- --------------------------------------------------------------
-- 4. 资源/权限
-- --------------------------------------------------------------
INSERT INTO resource (id, resource, resource_group, method, service_code, description, hidden, created_at, updated_at)
VALUES
(1, '/api/device/list', 'device', 'GET', 'device', '获取设备列表', false, NOW(), NOW()),
(2, '/api/device/create', 'device', 'POST', 'device', '创建设备', false, NOW(), NOW()),
(3, '/api/device/update', 'device', 'PUT', 'device', '更新设备', false, NOW(), NOW()),
(4, '/api/device/delete', 'device', 'DELETE', 'device', '删除设备', false, NOW(), NOW()),
(5, '/api/deployment/list', 'deployment', 'GET', 'deployment', '获取部署列表', false, NOW(), NOW()),
(6, '/api/deployment/create', 'deployment', 'POST', 'deployment', '创建部署', false, NOW(), NOW()),
(7, '/api/linkage/list', 'linkage', 'GET', 'linkage', '获取联动规则列表', false, NOW(), NOW()),
(8, '/api/linkage/create', 'linkage', 'POST', 'linkage', '创建联动规则', false, NOW(), NOW()),
(9, '/api/algorithm/list', 'algorithm', 'GET', 'algorithm', '获取算法列表', false, NOW(), NOW()),
(10, '/api/system/config', 'system', 'GET', 'system', '获取系统配置', false, NOW(), NOW());

SELECT setval('resource_id_seq', 10);

-- --------------------------------------------------------------
-- 5. 角色-资源绑定 (role_resource)
-- --------------------------------------------------------------
-- 管理员拥有所有资源
INSERT INTO role_resource (role_id, resource_id, created_at)
SELECT 1, id, NOW() FROM resource;

-- 操作员拥有读权限和部分写权限(不含删除)
INSERT INTO role_resource (role_id, resource_id, created_at)
SELECT 2, id, NOW() FROM resource WHERE method IN ('GET', 'POST', 'PUT') AND resource NOT LIKE '%delete%';

-- 访客仅拥有读权限
INSERT INTO role_resource (role_id, resource_id, created_at)
SELECT 3, id, NOW() FROM resource WHERE method = 'GET';

-- --------------------------------------------------------------
-- 6. 设备 (20个设备，分散在海东分公司org_id=2和西宁分公司org_id=3)
-- --------------------------------------------------------------
INSERT INTO device (id, device_code, name, status, access_type, device_type, longitude, latitude, region_id, org_id, memory_usage, disk_size, disk_usage, remark, created_at, updated_at)
VALUES
-- 海东分公司区域设备 (org_id=2, region_id=5/6)
(1, 'S201-HD-001', 'S201海东分公司K228+300下行(道路沿线)', 'active', 'rtsp', 'camera', 102.4012, 36.4823, 5, 2, 45.5, 32000, 23.1, '道路沿线高清摄像头', NOW(), NOW()),
(2, 'S201-HD-002', 'S201海东分公司K228+800上行(道路沿线)', 'active', 'rtsp', 'camera', 102.4035, 36.4831, 5, 2, 42.3, 32000, 21.5, '道路沿线高清摄像头', NOW(), NOW()),
(3, 'G213-HD-001', 'G213策磨高速乐化路段K16+250上行', 'active', 'rtsp', 'camera', 102.3891, 36.4672, 6, 2, 38.7, 16000, 18.2, '高速路上行摄像头', NOW(), NOW()),
(4, 'G213-HD-002', 'G213策磨高速乐化路段K16+800下行', 'active', 'rtsp', 'camera', 102.3912, 36.4655, 6, 2, 51.2, 32000, 25.6, '高速路下行摄像头', NOW(), NOW()),
(5, 'HD-TUN-001', '海东隧道入口K15+200', 'active', 'rtsp', 'camera', 102.3789, 36.4512, 6, 2, 33.4, 16000, 15.8, '隧道入口监控', NOW(), NOW()),
(6, 'HD-TUN-002', '海东隧道出口K17+100', 'active', 'rtsp', 'camera', 102.3821, 36.4489, 6, 2, 35.1, 16000, 16.2, '隧道出口监控', NOW(), NOW()),
(7, 'HD-YH-001', '海东养护中心A区', 'active', 'rtsp', 'camera', 102.3956, 36.4723, 2, 4, 28.9, 8000, 12.3, '养护中心A区监控', NOW(), NOW()),
(8, 'HD-YH-002', '海东养护中心B区', 'active', 'rtsp', 'camera', 102.3967, 36.4731, 2, 4, 30.2, 8000, 13.1, '养护中心B区监控', NOW(), NOW()),
-- 西宁分公司区域设备 (org_id=3, region_id=7/8)
(9, 'S201-XN-001', 'S201西宁段K45+100上行', 'active', 'rtsp', 'camera', 101.7789, 36.6234, 7, 3, 47.8, 32000, 22.4, '西宁段道路监控', NOW(), NOW()),
(10, 'S201-XN-002', 'S201西宁段K45+600下行', 'active', 'rtsp', 'camera', 101.7801, 36.6212, 7, 3, 44.5, 32000, 20.8, '西宁段道路监控', NOW(), NOW()),
(11, 'G213-XN-001', 'G213西宁段K88+200上行', 'active', 'rtsp', 'camera', 101.8123, 36.5891, 8, 3, 39.6, 16000, 17.5, '西宁高速监控', NOW(), NOW()),
(12, 'G213-XN-002', 'G213西宁段K88+700下行', 'active', 'rtsp', 'camera', 101.8145, 36.5878, 8, 3, 41.2, 16000, 18.9, '西宁高速监控', NOW(), NOW()),
-- 格尔木区域设备 (org_id=4, region_id=4)
(13, 'GEM-GS-001', '格尔木至拉萨方向K120+300', 'active', 'rtsp', 'camera', 94.9034, 36.4123, 4, 4, 52.1, 32000, 26.7, '进藏方向监控', NOW(), NOW()),
(14, 'GEM-GS-002', '格尔木至拉萨方向K121+100', 'active', 'rtsp', 'camera', 94.9156, 36.4089, 4, 4, 48.9, 32000, 23.8, '进藏方向监控', NOW(), NOW()),
-- 备用/维护设备
(15, 'MAINT-001', '海东维护站备用摄像头', 'inactive', 'rtsp', 'camera', 102.3878, 36.4698, 2, 2, 15.2, 8000, 8.5, '维护备用', NOW(), NOW()),
(16, 'MAINT-002', '西宁维护站备用摄像头', 'inactive', 'rtsp', 'camera', 101.7956, 36.6156, 3, 3, 16.8, 8000, 9.2, '维护备用', NOW(), NOW()),
-- 更多道路设备
(17, 'S201-EM-001', 'S201应急车道K230+500', 'active', 'rtsp', 'camera', 102.4089, 36.4856, 5, 2, 36.7, 16000, 17.1, '应急车道监控', NOW(), NOW()),
(18, 'G213-EM-001', 'G213应急车道K17+200', 'active', 'rtsp', 'camera', 102.3901, 36.4667, 6, 2, 37.4, 16000, 16.8, '应急车道监控', NOW(), NOW()),
(19, 'S201-TR-001', 'S201特情K50+100', 'active', 'rtsp', 'camera', 101.8012, 36.6289, 7, 3, 43.2, 32000, 21.2, '特情监控点', NOW(), NOW()),
(20, 'G213-TR-001', 'G213特情K90+300', 'active', 'rtsp', 'camera', 101.8256, 36.5834, 8, 3, 45.8, 32000, 22.9, '特情监控点', NOW(), NOW());

SELECT setval('device_id_seq', 20);

-- --------------------------------------------------------------
-- 7. 设备组 (6个组)
-- --------------------------------------------------------------
INSERT INTO device_group (id, group_code, name, device_count, remark, parent_id, created_at, updated_at)
VALUES
(1, 'HD-DG', '海东设备组', 8, '海东分公司管辖的所有设备', NULL, NOW(), NOW()),
(2, 'XN-DG', '西宁设备组', 6, '西宁分公司管辖的所有设备', NULL, NOW(), NOW()),
(3, 'ROAD-DG', '道路沿线组', 6, '道路沿线监控设备', NULL, NOW(), NOW()),
(4, 'TUNNEL-DG', '隧道组', 2, '隧道内监控设备', NULL, NOW(), NOW()),
(5, 'YH-DG', '养护中心组', 2, '养护中心内部监控', NULL, NOW(), NOW()),
(6, 'EMERG-DG', '应急车道组', 2, '应急车道监控设备', NULL, NOW(), NOW());

SELECT setval('device_group_id_seq', 6);

-- --------------------------------------------------------------
-- 8. 设备组-成员关系 (device_group_membership)
-- --------------------------------------------------------------
-- 海东设备组: 设备1-8
INSERT INTO device_group_membership (device_group_id, device_id, created_at)
SELECT 1, id, NOW() FROM device WHERE id <= 8;

-- 西宁设备组: 设备9-12, 19, 20
INSERT INTO device_group_membership (device_group_id, device_id, created_at)
SELECT 2, id, NOW() FROM device WHERE id IN (9, 10, 11, 12, 19, 20);

-- 道路沿线组: 设备1, 2, 3, 4, 9, 10
INSERT INTO device_group_membership (device_group_id, device_id, created_at)
SELECT 3, id, NOW() FROM device WHERE id IN (1, 2, 3, 4, 9, 10);

-- 隧道组: 设备5, 6
INSERT INTO device_group_membership (device_group_id, device_id, created_at)
SELECT 4, id, NOW() FROM device WHERE id IN (5, 6);

-- 养护中心组: 设备7, 8
INSERT INTO device_group_membership (device_group_id, device_id, created_at)
SELECT 5, id, NOW() FROM device WHERE id IN (7, 8);

-- 应急车道组: 设备17, 18
INSERT INTO device_group_membership (device_group_id, device_id, created_at)
SELECT 6, id, NOW() FROM device WHERE id IN (17, 18);

-- --------------------------------------------------------------
-- 9. 设备流 (device_stream) - 每个设备1个主码流
-- --------------------------------------------------------------
INSERT INTO device_stream (device_id, stream_type, stream_url, push_url, resolution, fps, codec, is_primary, status, created_at, updated_at)
SELECT id, 'main',
       'rtsp://192.168.1.'||(100+id)::text||'/live/stream'||id,
       'rtmp://192.168.1.'||(100+id)::text||'/live/stream'||id,
       '1920x1080', 25, 'H.264', true, 'active', NOW(), NOW()
FROM device;

-- --------------------------------------------------------------
-- 10. 算法服务 (3个服务)
-- --------------------------------------------------------------
INSERT INTO algorithm_service (id, service_id, service_name, service_code, service_ip, service_port, annotation_ip, annotation_port, status, created_at, updated_at)
VALUES
(1, 'SVC-001', '视频分析服务-1', 'algo-service-1', '192.168.1.101'::inet, 8554, '192.168.1.101'::inet, 8555, 'active', NOW(), NOW()),
(2, 'SVC-002', '视频分析服务-2', 'algo-service-2', '192.168.1.102'::inet, 8554, '192.168.1.102'::inet, 8555, 'active', NOW(), NOW()),
(3, 'SVC-003', '视频分析服务-3', 'algo-service-3', '192.168.1.103'::inet, 8554, '192.168.1.103'::inet, 8555, 'running', NOW(), NOW());

SELECT setval('algorithm_service_id_seq', 3);

-- --------------------------------------------------------------
-- 11. 联动规则 (10条规则)
-- --------------------------------------------------------------
INSERT INTO linkage_rule (id, rule_name, trigger_mode, algorithm_id, event_type_id, level, delay_push, is_compliant, unit, action_type, status, content, importance_level, push_channels, push_target, remark, created_at, updated_at)
VALUES
-- 交通相关规则
(1, '异常停车检测联动', 'AUTO', 11, 2, 3, 10, 'true', '次', 'alarm', 'active', '{"threshold": 5, "duration": 300}', 2, '["web","sms"]', '18600000001', '检测到异常停车时立即推送', NOW(), NOW()),
(2, '逆向行驶告警', 'AUTO', 11, 3, 4, 5, 'false', '次', 'alarm', 'active', '{"threshold": 1, "duration": 0}', 3, '["web","sms","email"]', '18600000002', '逆向行驶高危告警', NOW(), NOW()),
(3, '行人闯入联动', 'AUTO', 11, 4, 3, 15, 'true', '次', 'alarm', 'active', '{"threshold": 3, "duration": 180}', 2, '["web"]', '18600000003', '行人进入机动车道告警', NOW(), NOW()),
(4, '应急车道占用告警', 'AUTO', 11, 5, 3, 8, 'false', '次', 'alarm', 'active', '{"threshold": 2, "duration": 120}', 2, '["web","sms"]', '18600000004', '违规占用应急车道', NOW(), NOW()),
(5, '交通拥堵联动', 'AUTO', 11, 6, 2, 30, 'true', '辆/分钟', 'notification', 'active', '{"threshold": 20, "duration": 600}', 1, '["web"]', '18600000005', '道路拥堵提醒', NOW(), NOW()),
-- 安防相关规则
(6, '烟雾火灾检测', 'AUTO', 12, 8, 5, 3, 'false', '次', 'alarm', 'active', '{"threshold": 1, "duration": 0}', 4, '["web","sms","email"]', '18600000006', '烟雾火焰检测高危告警', NOW(), NOW()),
(7, '区域拥挤检测', 'AUTO', 6, 12, 3, 20, 'true', '人', 'notification', 'active', '{"threshold": 50, "duration": 300}', 2, '["web"]', '18600000007', '区域人员过于密集', NOW(), NOW()),
(8, '越界检测告警', 'AUTO', 8, 14, 3, 10, 'false', '次', 'alarm', 'active', '{"threshold": 1, "duration": 0}', 2, '["web","sms"]', '18600000008', '电子围栏入侵告警', NOW(), NOW()),
(9, '人员聚集告警', 'AUTO', 10, 15, 3, 25, 'true', '人', 'notification', 'active', '{"threshold": 20, "duration": 600}', 2, '["web"]', '18600000009', '人员异常聚集', NOW(), NOW()),
(10, '车牌识别记录', 'AUTO', 3, 1, 1, 60, 'true', '辆', 'log', 'active', '{"threshold": 100, "duration": 3600}', 1, '["web"]', NULL, '车牌识别数据记录', NOW(), NOW());

SELECT setval('linkage_rule_id_seq', 10);

-- --------------------------------------------------------------
-- 12. 联动规则-设备关联 (linkage_rule_device)
-- --------------------------------------------------------------
-- 规则1关联道路沿线设备1-4
INSERT INTO linkage_rule_device (linkage_rule_id, device_id, created_at)
SELECT 1, id, NOW() FROM device WHERE id IN (1, 2, 3, 4);

-- 规则2关联设备3,4,11,12(高速设备)
INSERT INTO linkage_rule_device (linkage_rule_id, device_id, created_at)
SELECT 2, id, NOW() FROM device WHERE id IN (3, 4, 11, 12);

-- 规则3关联设备1,2,9,10(道路设备)
INSERT INTO linkage_rule_device (linkage_rule_id, device_id, created_at)
SELECT 3, id, NOW() FROM device WHERE id IN (1, 2, 9, 10);

-- 规则4关联应急车道设备17,18
INSERT INTO linkage_rule_device (linkage_rule_id, device_id, created_at)
SELECT 4, id, NOW() FROM device WHERE id IN (17, 18);

-- 规则5关联所有设备
INSERT INTO linkage_rule_device (linkage_rule_id, device_id, created_at)
SELECT 5, id, NOW() FROM device;

-- 规则6(火灾)关联隧道设备5,6
INSERT INTO linkage_rule_device (linkage_rule_id, device_id, created_at)
SELECT 6, id, NOW() FROM device WHERE id IN (5, 6);

-- 规则7关联养护中心设备7,8
INSERT INTO linkage_rule_device (linkage_rule_id, device_id, created_at)
SELECT 7, id, NOW() FROM device WHERE id IN (7, 8);

-- 规则8关联所有设备
INSERT INTO linkage_rule_device (linkage_rule_id, device_id, created_at)
SELECT 8, id, NOW() FROM device;

-- 规则9关联设备9,10,19,20(西宁设备)
INSERT INTO linkage_rule_device (linkage_rule_id, device_id, created_at)
SELECT 9, id, NOW() FROM device WHERE id IN (9, 10, 19, 20);

-- 规则10关联设备1,3,9,11(重点监测点)
INSERT INTO linkage_rule_device (linkage_rule_id, device_id, created_at)
SELECT 10, id, NOW() FROM device WHERE id IN (1, 3, 9, 11);

-- --------------------------------------------------------------
-- 13. 部署 (5个部署)
-- --------------------------------------------------------------
INSERT INTO deployment (id, name, algorithm_id, service_id, status, algorithm_status, deployed_at, created_at, updated_at)
VALUES
(1, '海东道路监控部署', 11, 1, 'active', 'running', NOW() - INTERVAL '7 days', NOW(), NOW()),
(2, '西宁高速监控部署', 11, 2, 'active', 'running', NOW() - INTERVAL '5 days', NOW(), NOW()),
(3, '隧道火灾检测部署', 12, 1, 'active', 'running', NOW() - INTERVAL '3 days', NOW(), NOW()),
(4, '养护中心人流检测', 6, 2, 'active', 'running', NOW() - INTERVAL '2 days', NOW(), NOW()),
(5, '车牌识别采集', 3, 3, 'active', 'stopped', NOW() - INTERVAL '1 day', NOW(), NOW());

SELECT setval('deployment_id_seq', 5);

-- --------------------------------------------------------------
-- 14. 部署-设备关联 (deployment_device)
-- --------------------------------------------------------------
-- 部署1: 海东道路设备1-4
INSERT INTO deployment_device (deployment_id, device_id, created_at)
SELECT 1, id, NOW() FROM device WHERE id IN (1, 2, 3, 4);

-- 部署2: 西宁设备9-12
INSERT INTO deployment_device (deployment_id, device_id, created_at)
SELECT 2, id, NOW() FROM device WHERE id IN (9, 10, 11, 12);

-- 部署3: 隧道设备5,6
INSERT INTO deployment_device (deployment_id, device_id, created_at)
SELECT 3, id, NOW() FROM device WHERE id IN (5, 6);

-- 部署4: 养护中心设备7,8
INSERT INTO deployment_device (deployment_id, device_id, created_at)
SELECT 4, id, NOW() FROM device WHERE id IN (7, 8);

-- 部署5: 车牌识别设备1,3,9,11
INSERT INTO deployment_device (deployment_id, device_id, created_at)
SELECT 5, id, NOW() FROM device WHERE id IN (1, 3, 9, 11);

-- --------------------------------------------------------------
-- 15. 部署排期 (deployment_schedule)
-- --------------------------------------------------------------
-- 部署1: 工作日白天 7:00-20:00
INSERT INTO deployment_schedule (deployment_id, day_of_week, start_time, end_time, created_at, updated_at)
VALUES
(1, 1, '07:00:00', '20:00:00', NOW(), NOW()),
(1, 2, '07:00:00', '20:00:00', NOW(), NOW()),
(1, 3, '07:00:00', '20:00:00', NOW(), NOW()),
(1, 4, '07:00:00', '20:00:00', NOW(), NOW()),
(1, 5, '07:00:00', '20:00:00', NOW(), NOW());

-- 部署2: 全天候
INSERT INTO deployment_schedule (deployment_id, day_of_week, start_time, end_time, created_at, updated_at)
VALUES
(2, 0, '00:00:00', '23:59:59', NOW(), NOW()),
(2, 1, '00:00:00', '23:59:59', NOW(), NOW()),
(2, 2, '00:00:00', '23:59:59', NOW(), NOW()),
(2, 3, '00:00:00', '23:59:59', NOW(), NOW()),
(2, 4, '00:00:00', '23:59:59', NOW(), NOW()),
(2, 5, '00:00:00', '23:59:59', NOW(), NOW()),
(2, 6, '00:00:00', '23:59:59', NOW(), NOW());

-- 部署3: 隧道24小时
INSERT INTO deployment_schedule (deployment_id, day_of_week, start_time, end_time, created_at, updated_at)
SELECT 3, d, '00:00:00', '23:59:59', NOW(), NOW() FROM generate_series(0, 6) AS d;

-- --------------------------------------------------------------
-- 16. GB28181设备 (5个)
-- --------------------------------------------------------------
INSERT INTO gb28181_device (id, device_id, manufacturer, model, sip_server_id, sip_device_id, status, channels_json, created_at, updated_at)
VALUES
(1, 1, '海康威视', 'DS-2CD3T86FWDV2-I3', '34020000002000000001', '34020000001320000001', 'active', '[{"channelId": "34020000001320000001", "name": "主码流"}]'::jsonb, NOW(), NOW()),
(2, 3, '大华', 'DH-IPC-HFW8431E-Z', '34020000002000000002', '34020000001320000003', 'active', '[{"channelId": "34020000001320000003", "name": "主码流"}]'::jsonb, NOW(), NOW()),
(3, 5, '宇视科技', 'IPC2M4K', '34020000002000000003', '34020000001320000005', 'active', '[{"channelId": "34020000001320000005", "name": "主码流"}]'::jsonb, NOW(), NOW()),
(4, 9, '华为', 'M1221', '34020000002000000004', '34020000001320000009', 'active', '[{"channelId": "34020000001320000009", "name": "主码流"}]'::jsonb, NOW(), NOW()),
(5, 11, '海康威视', 'DS-2CD2T86FWDV2-I5', '34020000002000000005', '34020000001320000011', 'active', '[{"channelId": "34020000001320000011", "name": "主码流"}]'::jsonb, NOW(), NOW());

SELECT setval('gb28181_device_id_seq', 5);

-- --------------------------------------------------------------
-- 17. ONVIF设备 (5个)
-- --------------------------------------------------------------
INSERT INTO onvif_device (id, device_id, manufacturer, model, ip, port, status, profiles_json, created_at, updated_at)
VALUES
(1, 2, 'Axis', 'P3225-LVE', '192.168.1.102'::inet, 80, 'active', '[{"token": "profile1", "name": "MainStream"}]'::jsonb, NOW(), NOW()),
(2, 4, 'Bosch', 'NIN-50022', '192.168.1.104'::inet, 80, 'active', '[{"token": "profile1", "name": "MainStream"}]'::jsonb, NOW(), NOW()),
(3, 6, 'Axis', 'P3245-VE', '192.168.1.106'::inet, 80, 'active', '[{"token": "profile1", "name": "MainStream"}]'::jsonb, NOW(), NOW()),
(4, 10, 'Sony', 'SNC-XM640', '192.168.1.110'::inet, 80, 'active', '[{"token": "profile1", "name": "MainStream"}]'::jsonb, NOW(), NOW()),
(5, 12, 'Panasonic', 'WV-S2131', '192.168.1.112'::inet, 80, 'active', '[{"token": "profile1", "name": "MainStream"}]'::jsonb, NOW(), NOW());

SELECT setval('onvif_device_id_seq', 5);

-- --------------------------------------------------------------
-- 18. 摄像头预置位 (preset) - 10个
-- --------------------------------------------------------------
INSERT INTO preset (id, device_id, name, code, p, t, z, time_range_json, created_at, updated_at)
VALUES
(1, 1, '预置位1-全景', 'P01', 0.00, 0.00, 1.0, NULL, NOW(), NOW()),
(2, 1, '预置位2-近景', 'P02', 45.50, 30.20, 3.5, NULL, NOW(), NOW()),
(3, 3, '预置位1-主路', 'P01', 0.00, 0.00, 1.0, NULL, NOW(), NOW()),
(4, 3, '预置位2-应急车道', 'P02', 120.00, 15.00, 2.0, NULL, NOW(), NOW()),
(5, 5, '预置位1-入口', 'P01', 0.00, 0.00, 1.0, NULL, NOW(), NOW()),
(6, 5, '预置位2-出口', 'P02', 180.00, 0.00, 1.0, NULL, NOW(), NOW()),
(7, 9, '预置位1-主路', 'P01', 0.00, 0.00, 1.0, NULL, NOW(), NOW()),
(8, 9, '预置位2-路肩', 'P02', 90.00, 20.00, 2.5, NULL, NOW(), NOW()),
(9, 11, '预置位1-主路', 'P01', 0.00, 0.00, 1.0, NULL, NOW(), NOW()),
(10, 13, '预置位1-全景', 'P01', 0.00, 0.00, 1.0, NULL, NOW(), NOW());

SELECT setval('preset_id_seq', 10);

-- --------------------------------------------------------------
-- 19. 处置标签 (dispose_tag) - 5个
-- --------------------------------------------------------------
INSERT INTO dispose_tag (id, tag_name, tag_color, usage_count, remark, created_at, updated_at)
VALUES
(1, '已处理', '#67C23A', 45, '事件已处理完毕', NOW(), NOW()),
(2, '处理中', '#E6A23C', 23, '正在处理中', NOW(), NOW()),
(3, '待处理', '#909399', 67, '等待处理', NOW(), NOW()),
(4, '误报', '#F56C6C', 12, '确认为误报', NOW(), NOW()),
(5, '升级处理', '#409EFF', 8, '需要升级处理', NOW(), NOW());

SELECT setval('dispose_tag_id_seq', 5);

-- --------------------------------------------------------------
-- 20. 操作日志 (operation_log) - 20条
-- --------------------------------------------------------------
INSERT INTO operation_log (username, action, ip, result, module, action_time, created_at)
VALUES
('admin', '登录系统', '192.168.1.100'::inet, 'success', '认证', NOW() - INTERVAL '30 days', NOW() - INTERVAL '30 days'),
('admin', '创建设备:S201-HD-001', '192.168.1.100'::inet, 'success', '设备管理', NOW() - INTERVAL '25 days', NOW() - INTERVAL '25 days'),
('admin', '更新联动规则:异常停车检测', '192.168.1.100'::inet, 'success', '联动配置', NOW() - INTERVAL '20 days', NOW() - INTERVAL '20 days'),
('admin', '部署算法服务', '192.168.1.100'::inet, 'success', '算法管理', NOW() - INTERVAL '18 days', NOW() - INTERVAL '18 days'),
('admin', '删除设备:MAINT-001', '192.168.1.100'::inet, 'success', '设备管理', NOW() - INTERVAL '15 days', NOW() - INTERVAL '15 days'),
('admin', '修改系统配置', '192.168.1.100'::inet, 'success', '系统配置', NOW() - INTERVAL '12 days', NOW() - INTERVAL '12 days'),
('admin', '查看监控墙', '192.168.1.100'::inet, 'success', '视频监控', NOW() - INTERVAL '10 days', NOW() - INTERVAL '10 days'),
('admin', '导出操作日志', '192.168.1.100'::inet, 'success', '系统管理', NOW() - INTERVAL '8 days', NOW() - INTERVAL '8 days'),
('admin', '更新设备分组', '192.168.1.100'::inet, 'success', '设备管理', NOW() - INTERVAL '6 days', NOW() - INTERVAL '6 days'),
('admin', '配置排期计划', '192.168.1.100'::inet, 'success', '部署管理', NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days'),
('operator', '登录系统', '192.168.1.101'::inet, 'success', '认证', NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days'),
('operator', '查看设备列表', '192.168.1.101'::inet, 'success', '设备管理', NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days'),
('operator', '查看推送历史', '192.168.1.101'::inet, 'success', '联动配置', NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days'),
('operator', '标注监控区域', '192.168.1.101'::inet, 'success', '算法管理', NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days'),
('operator', '查询事件记录', '192.168.1.101'::inet, 'success', '事件管理', NOW() - INTERVAL '1 days', NOW() - INTERVAL '1 days'),
('admin', '批量导入设备', '192.168.1.100'::inet, 'success', '设备管理', NOW() - INTERVAL '22 days', NOW() - INTERVAL '22 days'),
('admin', '启动部署:海东道路监控', '192.168.1.100'::inet, 'success', '部署管理', NOW() - INTERVAL '7 days', NOW() - INTERVAL '7 days'),
('admin', '停止部署:车牌识别采集', '192.168.1.100'::inet, 'success', '部署管理', NOW() - INTERVAL '1 days', NOW() - INTERVAL '1 days'),
('admin', '更新固件版本', '192.168.1.100'::inet, 'success', '系统配置', NOW() - INTERVAL '14 days', NOW() - INTERVAL '14 days'),
('operator', '登出系统', '192.168.1.101'::inet, 'success', '认证', NOW() - INTERVAL '1 hours', NOW() - INTERVAL '1 hours');

-- --------------------------------------------------------------
-- 21. 任务 (task) - 5个
-- --------------------------------------------------------------
INSERT INTO task (id, task_name, trigger_type, trigger_rule, algorithm_id, status, last_run_time, created_at, updated_at)
VALUES
(1, '定时抽帧任务', 'cron', '0 */30 * * * *', 1, 'active', NOW() - INTERVAL '1 hours', NOW(), NOW()),
(2, '夜间分析任务', 'cron', '0 0 22 * * *', 5, 'active', NOW() - INTERVAL '12 hours', NOW(), NOW()),
(3, '交通检测日报', 'cron', '0 0 8 * * *', 11, 'active', NOW() - INTERVAL '20 hours', NOW(), NOW()),
(4, '设备状态巡检', 'cron', '0 */10 * * * *', 1, 'active', NOW() - INTERVAL '10 minutes', NOW(), NOW()),
(5, '事件统计汇总', 'cron', '0 0 0 * * *', 1, 'inactive', NULL, NOW(), NOW());

SELECT setval('task_id_seq', 5);

-- --------------------------------------------------------------
-- 22. 任务-设备关联 (task_device)
-- --------------------------------------------------------------
-- 任务1关联所有设备
INSERT INTO task_device (task_id, device_id, created_at)
SELECT 1, id, NOW() FROM device;

-- 任务2关联道路设备1-4,9-12,17-20
INSERT INTO task_device (task_id, device_id, created_at)
SELECT 2, id, NOW() FROM device WHERE id IN (1, 2, 3, 4, 9, 10, 11, 12, 17, 18, 19, 20);

-- 任务3关联所有设备
INSERT INTO task_device (task_id, device_id, created_at)
SELECT 3, id, NOW() FROM device;

-- 任务4关联所有设备
INSERT INTO task_device (task_id, device_id, created_at)
SELECT 4, id, NOW() FROM device;

-- 任务5关联主要设备1-10
INSERT INTO task_device (task_id, device_id, created_at)
SELECT 5, id, NOW() FROM device WHERE id <= 10;

-- --------------------------------------------------------------
-- 23. 推送历史 (push_history) - 15条
-- --------------------------------------------------------------
INSERT INTO push_history (id, rule_id, device_id, event_type_id, push_channels, push_target, push_time, status, retry_count, operator, count, detail, created_at)
VALUES
(1, 1, 1, 2, '["web","sms"]'::jsonb, '18600000001', NOW() - INTERVAL '2 days', 'success', 0, 'system', 1, '检测到异常停车', NOW() - INTERVAL '2 days'),
(2, 2, 3, 3, '["web","sms","email"]'::jsonb, '18600000002', NOW() - INTERVAL '2 days', 'success', 0, 'system', 1, '逆向行驶告警', NOW() - INTERVAL '2 days'),
(3, 4, 17, 5, '["web","sms"]'::jsonb, '18600000004', NOW() - INTERVAL '1 days', 'success', 0, 'system', 1, '应急车道占用', NOW() - INTERVAL '1 days'),
(4, 5, 9, 6, '["web"]'::jsonb, '18600000005', NOW() - INTERVAL '1 days', 'success', 0, 'system', 3, '交通拥堵', NOW() - INTERVAL '1 days'),
(5, 6, 5, 8, '["web","sms","email"]'::jsonb, '18600000006', NOW() - INTERVAL '12 hours', 'success', 0, 'system', 1, '烟雾检测', NOW() - INTERVAL '12 hours'),
(6, 7, 7, 12, '["web"]'::jsonb, '18600000007', NOW() - INTERVAL '6 hours', 'success', 0, 'system', 2, '区域拥挤', NOW() - INTERVAL '6 hours'),
(7, 8, 2, 14, '["web","sms"]'::jsonb, '18600000008', NOW() - INTERVAL '5 hours', 'success', 0, 'system', 1, '越界检测', NOW() - INTERVAL '5 hours'),
(8, 1, 4, 2, '["web","sms"]'::jsonb, '18600000001', NOW() - INTERVAL '4 hours', 'success', 0, 'system', 1, '异常停车', NOW() - INTERVAL '4 hours'),
(9, 9, 10, 15, '["web"]'::jsonb, '18600000009', NOW() - INTERVAL '3 hours', 'success', 0, 'system', 1, '人员聚集', NOW() - INTERVAL '3 hours'),
(10, 10, 1, 1, '["web"]'::jsonb, NULL, NOW() - INTERVAL '2 hours', 'success', 0, 'system', 5, '车牌识别', NOW() - INTERVAL '2 hours'),
(11, 3, 2, 4, '["web"]'::jsonb, '18600000003', NOW() - INTERVAL '1 hours', 'success', 0, 'system', 1, '行人闯入', NOW() - INTERVAL '1 hours'),
(12, 2, 11, 3, '["web","sms","email"]'::jsonb, '18600000002', NOW() - INTERVAL '30 minutes', 'failed', 2, 'system', 1, '逆向行驶', NOW() - INTERVAL '30 minutes'),
(13, 5, 12, 6, '["web"]'::jsonb, '18600000005', NOW() - INTERVAL '20 minutes', 'success', 0, 'system', 2, '交通拥堵', NOW() - INTERVAL '20 minutes'),
(14, 6, 6, 8, '["web","sms","email"]'::jsonb, '18600000006', NOW() - INTERVAL '10 minutes', 'success', 0, 'system', 1, '烟雾检测', NOW() - INTERVAL '10 minutes'),
(15, 1, 3, 2, '["web","sms"]'::jsonb, '18600000001', NOW() - INTERVAL '5 minutes', 'success', 0, 'system', 1, '异常停车', NOW() - INTERVAL '5 minutes');

SELECT setval('push_history_id_seq', 15);

-- --------------------------------------------------------------
-- 24. 清理记录 (clean_record) - 5条
-- --------------------------------------------------------------
INSERT INTO clean_record (id, type, cutoff_time, status, progress, clean_size_bytes, created_at, updated_at, created_by)
VALUES
(1, '日志清理', NOW() - INTERVAL '90 days', 'completed', 100.00, 1073741824, NOW() - INTERVAL '7 days', NOW() - INTERVAL '7 days', 1),
(2, '文件清理', NOW() - INTERVAL '180 days', 'completed', 100.00, 5368709120, NOW() - INTERVAL '14 days', NOW() - INTERVAL '14 days', 1),
(3, '事件归档', NOW() - INTERVAL '30 days', 'completed', 100.00, 2147483648, NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days', 1),
(4, '缓存清理', NOW() - INTERVAL '7 days', 'completed', 100.00, 1073741824, NOW() - INTERVAL '1 days', NOW() - INTERVAL '1 days', 1),
(5, '日志清理', NOW() - INTERVAL '90 days', 'running', 45.50, 536870912, NOW(), NOW(), 1);

SELECT setval('clean_record_id_seq', 5);

-- --------------------------------------------------------------
-- 25. 文件记录 (file) - 5条
-- --------------------------------------------------------------
INSERT INTO file (id, file_name, file_size_bytes, duration_seconds, device_id, file_type, storage_path, url, created_at, updated_at)
VALUES
(1, 'S201-HD-001_20240520_101020.mp4', 104857600, 60, 1, 'mp4', '/storage/video/2024/05/20/', 'http://192.168.1.200/video/S201-HD-001_20240520_101020.mp4', NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days'),
(2, 'G213-HD-001_20240521_145030.mp4', 209715200, 120, 3, 'mp4', '/storage/video/2024/05/21/', 'http://192.168.1.200/video/G213-HD-001_20240521_145030.mp4', NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days'),
(3, 'event_snapshot_001.jpg', 204800, NULL, 5, 'jpg', '/storage/snapshot/2024/05/20/', 'http://192.168.1.200/snapshot/event_snapshot_001.jpg', NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days'),
(4, 'S201-XN-001_20240522_083015.mp4', 157286400, 90, 9, 'mp4', '/storage/video/2024/05/22/', 'http://192.168.1.200/video/S201-XN-001_20240522_083015.mp4', NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days'),
(5, 'event_snapshot_002.jpg', 194560, NULL, 11, 'jpg', '/storage/snapshot/2024/05/21/', 'http://192.168.1.200/snapshot/event_snapshot_002.jpg', NOW() - INTERVAL '1 days', NOW() - INTERVAL '1 days');

SELECT setval('file_id_seq', 5);

-- --------------------------------------------------------------
-- 26. 固件记录 (firmware) - 3条
-- --------------------------------------------------------------
INSERT INTO firmware (id, name, version, applicable_version, force_upgrade, description, created_at, updated_at)
VALUES
(1, '摄像头固件v2.1.0', '2.1.0', '2.0.x', false, '修复夜间噪点问题，提升低照度表现', NOW() - INTERVAL '30 days', NOW() - INTERVAL '30 days'),
(2, '摄像头固件v2.1.2', '2.1.2', '2.0.x', true, '安全漏洞修复，必须升级', NOW() - INTERVAL '7 days', NOW() - INTERVAL '7 days'),
(3, 'NVR固件v3.2.0', '3.2.0', '3.1.x', false, '新增Onvif Profile S支持', NOW() - INTERVAL '14 days', NOW() - INTERVAL '14 days');

SELECT setval('firmware_id_seq', 3);

-- --------------------------------------------------------------
-- 27. License记录 (license) - 1条
-- --------------------------------------------------------------
INSERT INTO license (id, license_key, type, device_limit, used_count, expire_date, status, created_at, updated_at)
VALUES (1, 'QH-JT-2024-PRO-1000-DEVICES', 'enterprise', 1000, 20, '2025-12-31', 'active', NOW(), NOW());

SELECT setval('license_id_seq', 1);

-- --------------------------------------------------------------
-- 28. 微服务 (microservice) - 3条
-- --------------------------------------------------------------
INSERT INTO microservice (id, name, service_name, ip, port, status, cpu_usage, memory_usage, created_at, updated_at)
VALUES
(1, '设备接入服务', 'device-service', '192.168.1.201'::inet, 8080, 'active', 35.5, 48.2, NOW(), NOW()),
(2, '视频处理服务', 'video-service', '192.168.1.202'::inet, 8081, 'active', 62.3, 71.5, NOW(), NOW()),
(3, '事件分析服务', 'event-service', '192.168.1.203'::inet, 8082, 'active', 28.7, 35.9, NOW(), NOW());

SELECT setval('microservice_id_seq', 3);

-- --------------------------------------------------------------
-- 29. 视频标注 (annotation) - 5条
-- --------------------------------------------------------------
INSERT INTO annotation (id, deployment_id, device_id, name, type, polygon_json, color, created_at, updated_at)
VALUES
(1, 1, 1, '道路区域标注', 'monitoring', '[{"x":0.1,"y":0.1},{"x":0.9,"y":0.1},{"x":0.9,"y":0.9},{"x":0.1,"y":0.9}]'::jsonb, '#00FF00', NOW(), NOW()),
(2, 1, 2, '应急车道标注', 'forbidden', '[{"x":0.0,"y":0.4},{"x":0.3,"y":0.4},{"x":0.3,"y":0.6},{"x":0.0,"y":0.6}]'::jsonb, '#FF0000', NOW(), NOW()),
(3, 3, 5, '隧道入口标注', 'monitoring', '[{"x":0.2,"y":0.2},{"x":0.8,"y":0.2},{"x":0.8,"y":0.8},{"x":0.2,"y":0.8}]'::jsonb, '#00FF00', NOW(), NOW()),
(4, 2, 9, '道路区域标注', 'monitoring', '[{"x":0.1,"y":0.1},{"x":0.9,"y":0.1},{"x":0.9,"y":0.9},{"x":0.1,"y":0.9}]'::jsonb, '#00FF00', NOW(), NOW()),
(5, 4, 7, '养护区域标注', 'monitoring', '[{"x":0.15,"y":0.15},{"x":0.85,"y":0.15},{"x":0.85,"y":0.85},{"x":0.15,"y":0.85}]'::jsonb, '#00FF00', NOW(), NOW());

SELECT setval('annotation_id_seq', 5);

-- --------------------------------------------------------------
-- 30. 弹窗事件限制 (popup_event_limit) - 5条
-- --------------------------------------------------------------
INSERT INTO popup_event_limit (id, device_id, time_interval_seconds, response_mode, enabled, created_at, updated_at)
VALUES
(1, 1, 30, 'immediate', true, NOW(), NOW()),
(2, 3, 60, 'delayed', true, NOW(), NOW()),
(3, 5, 10, 'immediate', true, NOW(), NOW()),
(4, 9, 45, 'silent', true, NOW(), NOW()),
(5, 11, 30, 'immediate', true, NOW(), NOW());

SELECT setval('popup_event_limit_id_seq', 5);

-- --------------------------------------------------------------
-- 完成提示
-- --------------------------------------------------------------
DO $$
BEGIN
    RAISE NOTICE 'V3__seed_comprehensive.sql executed successfully';
END $$;