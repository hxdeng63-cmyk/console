UPDATE access_platform SET
  name = CASE id
    WHEN 2 THEN '海东GB28181平台'
    WHEN 3 THEN '西宁GB28181平台'
    WHEN 4 THEN '格尔木GB28181平台'
    WHEN 5 THEN 'Axis ONVIF平台'
    WHEN 6 THEN 'Bosch ONVIF平台'
  END,
  type = CASE
    WHEN id IN (2,3,4) THEN 'GB28181'
    WHEN id IN (5,6) THEN 'ONVIF'
  END,
  version = CASE id
    WHEN 2 THEN 'GB28181平台V2.0'
    WHEN 3 THEN 'GB28181平台V1.5'
    WHEN 4 THEN 'GB28181平台V2.1'
    WHEN 5 THEN 'ONVIF Profile S'
    WHEN 6 THEN 'ONVIF Profile G'
  END,
  config_json = CASE id
    WHEN 2 THEN '{"domain": "3402000000", "realm": "3402000000"}'::jsonb
    WHEN 3 THEN '{"domain": "3402000001", "realm": "3402000001"}'::jsonb
    WHEN 4 THEN '{"domain": "3402000002", "realm": "3402000002"}'::jsonb
    WHEN 5 THEN '{"username": "admin", "password": "axis123"}'::jsonb
    WHEN 6 THEN '{"username": "admin", "password": "bosch456"}'::jsonb
  END,
  updated_at = NOW()
WHERE id IN (2,3,4,5,6);

SELECT setval('access_platform_id_seq', 6);
