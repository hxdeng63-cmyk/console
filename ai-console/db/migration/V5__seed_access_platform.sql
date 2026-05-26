INSERT INTO access_platform (id, name, type, version, device_count, status, config_json, created_at, updated_at)
VALUES
(2, '海东GB28181平台', 'GB28181', 'GB28181平台V2.0', 0, 'active', '{"domain": "3402000000", "realm": "3402000000"}'::jsonb, NOW(), NOW()),
(3, '西宁GB28181平台', 'GB28181', 'GB28181平台V1.5', 0, 'active', '{"domain": "3402000001", "realm": "3402000001"}'::jsonb, NOW(), NOW()),
(4, '格尔木GB28181平台', 'GB28181', 'GB28181平台V2.1', 0, 'active', '{"domain": "3402000002", "realm": "3402000002"}'::jsonb, NOW(), NOW()),
(5, 'Axis ONVIF平台', 'ONVIF', 'ONVIF Profile S', 0, 'active', '{"username": "admin", "password": "axis123"}'::jsonb, NOW(), NOW()),
(6, 'Bosch ONVIF平台', 'ONVIF', 'ONVIF Profile G', 0, 'active', '{"username": "admin", "password": "bosch456"}'::jsonb, NOW(), NOW());

SELECT setval('access_platform_id_seq', 6);
