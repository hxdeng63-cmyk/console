INSERT INTO access_platform (id, name, type, version, device_count, status, config_json, created_at, updated_at)
VALUES
(4, 'E6B9BEEF2979GB28181E5B9B3E58F0E58F91', 'GB28181', 'GB28181E5B9B3E58F0V2.1', 0, 'active', '{"domain": "3402000002", "realm": "3402000002"}'::jsonb, NOW(), NOW()),
(5, 'Axis ONVIFE5B9B3E58F0', 'ONVIF', 'ONVIF Profile S', 0, 'active', '{"username": "admin", "password": "axis123"}'::jsonb, NOW(), NOW()),
(6, 'Bosch ONVIFE5B9B3E58F0', 'ONVIF', 'ONVIF Profile G', 0, 'active', '{"username": "admin", "password": "bosch456"}'::jsonb, NOW(), NOW())
ON CONFLICT DO NOTHING;

SELECT setval('access_platform_id_seq', 6);
