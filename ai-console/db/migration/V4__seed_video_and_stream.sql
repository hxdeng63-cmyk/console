-- V4__seed_video_and_stream.sql
-- Seed video_setting and device_stream tables

INSERT INTO video_setting (device_id, event_types, record_duration_seconds, status) VALUES
(1, '["异常停车", "逆向行驶", "行人闯入"]', 10, true),
(2, '["烟雾", "火灾"]', 8, true),
(3, '["作业人员", "作业车辆识别"]', 12, false),
(4, '["交通阻塞", "异常停车"]', 6, true),
(5, '["烟雾", "火灾", "越界检测"]', 10, true),
(6, '["遗留物检测", "行人闯入"]', 8, true),
(7, '["逆向行驶", "占用应急车道"]', 6, true),
(8, '["作业车辆识别", "非机动车驶入"]', 10, false),
(9, '["烟雾", "火灾"]', 12, true),
(10, '["异常停车", "交通阻塞"]', 8, true);

SELECT setval('video_setting_id_seq', 10);

INSERT INTO device_stream (device_id, stream_type, stream_url, is_primary, status) VALUES
(1, 'main', 'rtsp://192.168.10.1:554/stream1', true, 'active'),
(2, 'main', 'rtsp://192.168.10.2:554/stream1', true, 'active'),
(3, 'main', 'rtsp://192.168.10.3:554/stream1', true, 'inactive'),
(4, 'main', 'rtsp://192.168.10.4:554/stream1', true, 'active'),
(5, 'main', 'rtsp://192.168.10.5:554/stream1', true, 'active'),
(6, 'main', 'rtsp://192.168.10.6:554/stream1', true, 'inactive'),
(7, 'main', 'rtsp://192.168.10.7:554/stream1', true, 'active'),
(8, 'main', 'rtsp://192.168.10.8:554/stream1', true, 'active'),
(9, 'main', 'rtsp://192.168.10.9:554/stream1', true, 'inactive'),
(10, 'main', 'rtsp://192.168.10.10:554/stream1', true, 'active'),
(11, 'main', 'rtsp://192.168.11.1:554/stream1', true, 'active'),
(12, 'main', 'rtsp://192.168.11.2:554/stream1', true, 'active'),
(13, 'main', 'rtsp://192.168.11.3:554/stream1', true, 'inactive'),
(14, 'main', 'rtsp://192.168.11.4:554/stream1', true, 'active'),
(15, 'main', 'rtsp://192.168.11.5:554/stream1', true, 'active'),
(16, 'main', 'rtsp://192.168.11.6:554/stream1', true, 'inactive'),
(17, 'main', 'rtsp://192.168.11.7:554/stream1', true, 'active'),
(18, 'main', 'rtsp://192.168.11.8:554/stream1', true, 'active'),
(19, 'main', 'rtsp://192.168.11.9:554/stream1', true, 'inactive'),
(20, 'main', 'rtsp://192.168.11.10:554/stream1', true, 'active');

SELECT setval('device_stream_id_seq', 20);
