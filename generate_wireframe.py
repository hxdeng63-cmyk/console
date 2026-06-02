import random
from datetime import datetime, timedelta

random.seed(42)

org = '海东公司'
devices = [
    {'id': 51, 'name': '设备1', 'region': '南区', 'parent_region': '大学城南'},
    {'id': 52, 'name': '设备2', 'region': '南区', 'parent_region': '大学城南'},
    {'id': 53, 'name': '设备3', 'region': '南区', 'parent_region': '大学城南'},
    {'id': 54, 'name': '设备1', 'region': '北区', 'parent_region': '大学城北'},
]

event_types = [
    ('疑似事故', 5), ('作业人员', 3), ('交通阻塞', 3), ('异常停车', 4),
    ('烟雾', 2), ('作业车辆识别', 3), ('非机动车驶入', 2), ('占用应急车道', 5),
    ('逆向行驶', 3), ('通过卡车数量', 3), ('通过大客车数量', 2), ('通过摩托车数量', 5),
    ('通过小汽车数量', 2), ('下行车流量', 3), ('上行车流量', 5), ('行人闯入', 4)
]

linkage_rules = [
    (1, '疑似事故', 'webhook'), (2, '异常停车', 'push'), (3, '作业人员', 'email'),
    (4, '交通阻塞', 'snapshot'), (5, '烟雾', 'push'), (6, '行人闯入', 'webhook'),
    (7, '占用应急车道', 'email'), (8, '逆向行驶', 'snapshot'), (9, '通过卡车数量', 'push')
]

status_map = {'pending': '待处理', 'processing': '处理中', 'resolved': '已解决', 'ignored': '已忽略'}
severity_map = {1: '低', 2: '低', 3: '中', 4: '高', 5: '严重'}

local_images = [
    '/uploads/2026/06/00000.jpg',
    '/uploads/2026/06/0a96c6d2-ed93-4dec-8562-1c69af136ca7.jpg',
    '/uploads/2026/06/_91753989_capture.jpg',
]
local_videos = [
    '/uploads/2026/06/165c962d08838f11f572cb4b3e54135b.mp4',
    '/uploads/2026/06/4beb2aca90d91fa4d4b3e5007a4bbd52.mp4',
    '/uploads/2026/06/aea14d4b5df2f1b43eaa2e3c747a2808.mp4',
]

events = []
now = datetime(2026, 6, 2, 10, 0, 0)

for device in devices:
    count = random.randint(5, 8)
    for i in range(count):
        et_name, severity = random.choice(event_types)
        matched_rules = [r for r in linkage_rules if r[1] == et_name]
        if matched_rules:
            rule = random.choice(matched_rules)
        else:
            rule = (random.randint(10, 25), et_name, 'push')

        status = random.choice(list(status_map.keys()))
        report_time = now - timedelta(hours=random.randint(1, 168), minutes=random.randint(0, 59))

        idx = len(events)
        if idx >= 9:
            image_url = f'https://picsum.photos/seed/{idx}/400/300'
            video_url = f'https://picsum.photos/seed/{idx+100}/400/300'
        else:
            image_url = local_images[idx % len(local_images)]
            video_url = local_videos[idx % len(local_videos)]

        events.append({
            'id': idx + 1,
            'company': org,
            'region': f"{device['parent_region']} - {device['region']}",
            'device': device['name'],
            'algorithm': '交通算法',
            'event_type': et_name,
            'severity': severity_map[severity],
            'status': status_map[status],
            'status_code': status,
            'report_time': report_time.strftime('%Y-%m-%d %H:%M:%S'),
            'image': image_url,
            'video': video_url,
            'detail': f"{device['parent_region']}{device['region']}{device['name']}检测到{et_name}"
        })

print(f'总共生成 {len(events)} 条模拟预警事件\n')

# 列表视图
print('=' * 120)
print('【线框图 1】预警事件 - 列表视图')
print('=' * 120)
print()
print('┌' + '─' * 118 + '┐')
print('│  预警事件' + ' ' * 50 + '[列表视图] [图片视图]' + ' ' * 10 + '[导出] [批量处理]' + ' ' * 8 + '│')
print('├' + '─' * 118 + '┤')
print('│  公司名称: [海东公司 ▼]  区域: [全部 ▼]  算法: [全部 ▼]  事件类型: [全部 ▼]  设备名称: [全部 ▼]  处理状态: [全部 ▼]' + ' ' * 4 + '│')
print('│  时间范围: [2026-06-01] ~ [2026-06-02]' + ' ' * 45 + '[查询] [重置]' + ' ' * 10 + '│')
print('├' + '─' * 118 + '┤')
print('│' + ' ' * 118 + '│')
print(f'│  共 {len(events)} 条  每页 10 条    1 / {(len(events)+9)//10} 页    [首页] [上一页] [1] [2] [3] [下一页] [尾页]' + ' ' * 28 + '│')
print('│' + ' ' * 118 + '│')
print('│  ┌────┬───────────┬─────────────────┬──────────┬──────────┬────────────┬────────┬──────────┬─────────────────┬──────┐' + ' ' * 4 + '│')
print('│  │ 选择│ 公司名称  │      区域       │ 设备名称 │  算法    │  事件类型  │  等级  │ 处理状态 │    上报时间     │ 操作 │' + ' ' * 4 + '│')
print('│  ├────┼───────────┼─────────────────┼──────────┼──────────┼────────────┼────────┼──────────┼─────────────────┼──────┤' + ' ' * 4 + '│')

for e in events[:10]:
    sc = {'待处理': '🔴', '处理中': '🟡', '已解决': '🟢', '已忽略': '⚪'}.get(e['status'], '')
    print(f"│  │ [ ] │ {e['company']:<8} │ {e['region']:<15} │ {e['device']:<8} │ {e['algorithm']:<8} │ {e['event_type']:<10} │ {e['severity']:<6} │ {sc}{e['status']:<6}│ {e['report_time']} │ 详情 │   │")

print('│  └────┴───────────┴─────────────────┴──────────┴──────────┴────────────┴────────┴──────────┴─────────────────┴──────┘' + ' ' * 4 + '│')
print('│' + ' ' * 118 + '│')
print('└' + '─' * 118 + '┘')
print()

# 图片视图
print('=' * 120)
print('【线框图 2】预警事件 - 图片视图')
print('=' * 120)
print()
print('┌' + '─' * 118 + '┐')
print('│  预警事件' + ' ' * 50 + '[列表视图] [图片视图]' + ' ' * 10 + '[导出] [批量处理]' + ' ' * 8 + '│')
print('├' + '─' * 118 + '┤')
print('│  筛选条件同上...' + ' ' * 102 + '│')
print('├' + '─' * 118 + '┤')
print('│' + ' ' * 118 + '│')
print(f'│  共 {len(events)} 条  每页 8 条    1 / {(len(events)+7)//8} 页' + ' ' * 67 + '│')
print('│' + ' ' * 118 + '│')

for i in range(0, min(8, len(events)), 4):
    row = events[i:i+4]
    print('│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │')
    for _ in row:
        print('│  │ [图片预览区域]  │  │ [图片预览区域]  │  │ [图片预览区域]  │  │ [图片预览区域]  │   │')
    print('│  │                 │  │                 │  │                 │  │                 │   │')
    for e in row:
        print(f"│  │ {e['event_type']:<15} │  │ {e['event_type']:<15} │  │ {e['event_type']:<15} │  │ {e['event_type']:<15} │   │")
    for e in row:
        print(f"│  │ {e['device']} {e['region']:<10} │  │ {e['device']} {e['region']:<10} │  │ {e['device']} {e['region']:<10} │  │ {e['device']} {e['region']:<10} │   │")
    for e in row:
        sc = {'待处理': '🔴', '处理中': '🟡', '已解决': '🟢', '已忽略': '⚪'}.get(e['status'], '')
        t = e['report_time'][5:16]
        print(f"│  │ {sc}{e['status']:<10} {t}│  │ {sc}{e['status']:<10} {t}│  │ {sc}{e['status']:<10} {t}│  │ {sc}{e['status']:<10} {t}│   │")
    print('│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘   │')
    print('│' + ' ' * 85 + '│')

print('│' + ' ' * 118 + '│')
print('└' + '─' * 118 + '┘')
print()

# 详情弹窗
print('=' * 120)
print('【线框图 3】预警事件详情弹窗')
print('=' * 120)
print()
print('┌' + '─' * 79 + '┐')
print('│  预警事件详情' + ' ' * 55 + '[X]' + ' ' * 4 + '│')
print('├' + '─' * 79 + '┤')
print('│' + ' ' * 79 + '│')
print('│  ┌─────────────────────────┐  ┌─────────────────────────────────┐   │')
print('│  │                         │  │  事件信息                       │   │')
print('│  │    [抓拍图片预览区域]    │  │                                 │   │')
print('│  │                         │  │  公司名称: 海东公司              │   │')
print('│  │      400 x 300          │  │  所属区域: 大学城南 - 南区       │   │')
print('│  │                         │  │  设备名称: 设备1                 │   │')
print('│  │                         │  │  算法名称: 交通算法              │   │')
print('│  └─────────────────────────┘  │  事件类型: 疑似事故              │   │')
print('│                               │  事件等级: 严重                  │   │')
print('│  ┌─────────────────────────┐  │  处理状态: 待处理                │   │')
print('│  │                         │  │  上报时间: 2026-06-01 08:23:15   │   │')
print('│  │    [视频播放区域]        │  │                                 │   │')
print('│  │                         │  │  联动规则: 联动规则-01 (webhook) │   │')
print('│  │   点击播放录像片段       │  │                                 │   │')
print('│  │                         │  │  事件详情:                       │   │')
print('│  └─────────────────────────┘  │  大学城南南区设备1检测到疑似事故   │   │')
print('│                               │                                 │   │')
print('│                               │  [标记为已处理] [忽略] [导出]    │   │')
print('│                               │                                 │   │')
print('└' + '─' * 79 + '┘')
print()

# 数据统计
from collections import Counter
status_counts = Counter(e['status'] for e in events)
region_counts = Counter(e['region'] for e in events)
et_counts = Counter(e['event_type'] for e in events)

print('=' * 120)
print('【数据统计】')
print('=' * 120)
print()
print(f'总预警事件数: {len(events)} 条')
print()
print('按处理状态分布:')
for s, c in status_counts.most_common():
    print(f'  {s}: {c} 条')
print()
print('按区域分布:')
for r, c in region_counts.most_common():
    print(f'  {r}: {c} 条')
print()
print('按事件类型分布 (Top 5):')
for et, c in et_counts.most_common(5):
    print(f'  {et}: {c} 条')
print()
print('图片路径分布:')
local_count = sum(1 for e in events if e['image'].startswith('/uploads'))
external_count = sum(1 for e in events if e['image'].startswith('http'))
print(f'  本地图片: {local_count} 条')
print(f'  外部URL: {external_count} 条')
