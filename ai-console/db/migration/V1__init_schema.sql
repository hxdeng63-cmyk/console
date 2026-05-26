-- ============================================================
-- Flyway Versioned Migration: V1__init_schema
-- 创建 AI Console 完整数据库 Schema
-- 执行一次，不可逆（Community 版无 Undo，需手动回滚）
-- ============================================================

-- --------------------------------------------------------------
-- 0. 扩展
-- --------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- --------------------------------------------------------------
-- 1. 通用函数
-- --------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- --------------------------------------------------------------
-- 2. 权限域
-- --------------------------------------------------------------

CREATE TABLE organization (
    id              BIGSERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    parent_id       BIGINT REFERENCES organization(id),
    level           INT DEFAULT 1,
    sort            INT DEFAULT 0,
    code            VARCHAR(50),
    remark          VARCHAR(500),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by      BIGINT,
    updated_by      BIGINT,
    deleted_at      TIMESTAMP WITH TIME ZONE,
    CONSTRAINT chk_organization_no_self_parent CHECK (parent_id IS NULL OR parent_id != id)
);

CREATE INDEX idx_organization_parent ON organization(parent_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_organization_level   ON organization(level)   WHERE deleted_at IS NULL;

CREATE TRIGGER trg_organization_updated_at
BEFORE UPDATE ON organization FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- user
CREATE TABLE "user" (
    id              BIGSERIAL PRIMARY KEY,
    username        VARCHAR(50) NOT NULL,
    real_name       VARCHAR(50),
    password        VARCHAR(255) NOT NULL,
    avatar          VARCHAR(500),
    phone           VARCHAR(20),
    email           VARCHAR(100),
    gender          VARCHAR(10),
    org_id          BIGINT REFERENCES organization(id),
    status          VARCHAR(20) DEFAULT 'active' NOT NULL,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by      BIGINT,
    updated_by      BIGINT,
    deleted_at      TIMESTAMP WITH TIME ZONE,
    CONSTRAINT chk_user_status CHECK (status IN ('active', 'inactive')),
    CONSTRAINT uq_user_username UNIQUE (username)
);

CREATE INDEX idx_user_org    ON "user"(org_id)  WHERE deleted_at IS NULL;
CREATE INDEX idx_user_status ON "user"(status) WHERE deleted_at IS NULL;

CREATE TRIGGER trg_user_updated_at
BEFORE UPDATE ON "user" FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- role
CREATE TABLE role (
    id              BIGSERIAL PRIMARY KEY,
    name            VARCHAR(50) NOT NULL,
    code            VARCHAR(50),
    description     VARCHAR(255),
    status          VARCHAR(20) DEFAULT 'active' NOT NULL,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by      BIGINT,
    updated_by      BIGINT,
    deleted_at      TIMESTAMP WITH TIME ZONE,
    CONSTRAINT chk_role_status CHECK (status IN ('active', 'inactive'))
);

CREATE TRIGGER trg_role_updated_at
BEFORE UPDATE ON role FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- menu
CREATE TABLE menu (
    id              BIGSERIAL PRIMARY KEY,
    name            VARCHAR(50) NOT NULL,
    path            VARCHAR(200),
    hidden          BOOLEAN DEFAULT false,
    parent_id       BIGINT REFERENCES menu(id),
    sort            INT DEFAULT 0,
    component       VARCHAR(200),
    title           VARCHAR(100),
    icon            VARCHAR(100),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by      BIGINT,
    updated_by      BIGINT,
    deleted_at      TIMESTAMP WITH TIME ZONE,
    CONSTRAINT chk_menu_no_self_parent CHECK (parent_id IS NULL OR parent_id != id)
);

CREATE INDEX idx_menu_parent ON menu(parent_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_menu_sort   ON menu(sort)     WHERE deleted_at IS NULL;

CREATE TRIGGER trg_menu_updated_at
BEFORE UPDATE ON menu FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- resource
CREATE TABLE resource (
    id              BIGSERIAL PRIMARY KEY,
    resource        VARCHAR(200) NOT NULL,
    resource_group  VARCHAR(100) NOT NULL,
    method          VARCHAR(20) DEFAULT 'GET',
    service_code    VARCHAR(50),
    description     VARCHAR(255),
    hidden          BOOLEAN DEFAULT false,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by      BIGINT,
    updated_by      BIGINT,
    deleted_at      TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_resource_group ON resource(resource_group) WHERE deleted_at IS NULL;

CREATE TRIGGER trg_resource_updated_at
BEFORE UPDATE ON resource FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- --------------------------------------------------------------
-- 3. 权限连接表
-- --------------------------------------------------------------

CREATE TABLE user_role (
    user_id     BIGINT NOT NULL REFERENCES "user"(id),
    role_id     BIGINT NOT NULL REFERENCES role(id),
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE role_menu (
    role_id     BIGINT NOT NULL REFERENCES role(id),
    menu_id     BIGINT NOT NULL REFERENCES menu(id),
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (role_id, menu_id)
);

CREATE TABLE role_resource (
    role_id     BIGINT NOT NULL REFERENCES role(id),
    resource_id BIGINT NOT NULL REFERENCES resource(id),
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (role_id, resource_id)
);

-- --------------------------------------------------------------
-- 4. 设备管理域
-- --------------------------------------------------------------

CREATE TABLE region (
    id          BIGSERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    code        VARCHAR(50),
    parent_id   BIGINT REFERENCES region(id),
    level       INT DEFAULT 1,
    sort        INT DEFAULT 0,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by  BIGINT,
    updated_by  BIGINT,
    deleted_at  TIMESTAMP WITH TIME ZONE,
    CONSTRAINT chk_region_no_self_parent CHECK (parent_id IS NULL OR parent_id != id)
);

CREATE INDEX idx_region_parent ON region(parent_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_region_code   ON region(code)     WHERE deleted_at IS NULL;

CREATE TRIGGER trg_region_updated_at
BEFORE UPDATE ON region FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE device (
    id              BIGSERIAL PRIMARY KEY,
    device_code     VARCHAR(32) NOT NULL,
    name            VARCHAR(255) NOT NULL,
    status          VARCHAR(20) DEFAULT 'active' NOT NULL,
    access_type     VARCHAR(20) DEFAULT 'direct' NOT NULL,
    device_type     VARCHAR(50),
    longitude       DECIMAL(10, 7),
    latitude        DECIMAL(10, 7),
    region_id       BIGINT REFERENCES region(id),
    org_id          BIGINT REFERENCES organization(id),
    memory_usage    DECIMAL(5, 2),
    disk_size       BIGINT,
    disk_usage      DECIMAL(5, 2),
    remark          VARCHAR(500),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by      BIGINT,
    updated_by      BIGINT,
    deleted_at      TIMESTAMP WITH TIME ZONE,
    CONSTRAINT chk_device_status CHECK (status IN ('active', 'inactive')),
    CONSTRAINT chk_device_access_type CHECK (access_type IN ('rtsp', 'gb28181', 'onvif', 'internal', 'direct', 'rtmp')),
    CONSTRAINT uq_device_code_access UNIQUE (device_code, access_type)
);

CREATE INDEX idx_device_region      ON device(region_id)   WHERE deleted_at IS NULL;
CREATE INDEX idx_device_org         ON device(org_id)      WHERE deleted_at IS NULL;
CREATE INDEX idx_device_status      ON device(status)      WHERE deleted_at IS NULL;
CREATE INDEX idx_device_access_type ON device(access_type) WHERE deleted_at IS NULL;

CREATE TRIGGER trg_device_updated_at
BEFORE UPDATE ON device FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE device_stream (
    id              BIGSERIAL PRIMARY KEY,
    device_id       BIGINT NOT NULL REFERENCES device(id),
    stream_type     VARCHAR(20) DEFAULT 'main',
    stream_url      VARCHAR(500),
    push_url        VARCHAR(500),
    resolution      VARCHAR(20),
    fps             INT,
    codec           VARCHAR(20),
    is_primary      BOOLEAN DEFAULT false,
    status          VARCHAR(20) DEFAULT 'active',
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by      BIGINT,
    updated_by      BIGINT,
    deleted_at      TIMESTAMP WITH TIME ZONE,
    CONSTRAINT chk_stream_status CHECK (status IN ('active', 'inactive')),
    CONSTRAINT uq_device_primary_stream UNIQUE (device_id, is_primary)
);

CREATE INDEX idx_device_stream_device   ON device_stream(device_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_device_stream_primary  ON device_stream(device_id, is_primary) WHERE deleted_at IS NULL;

CREATE TRIGGER trg_device_stream_updated_at
BEFORE UPDATE ON device_stream FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE device_group (
    id              BIGSERIAL PRIMARY KEY,
    group_code      VARCHAR(50),
    name            VARCHAR(100) NOT NULL,
    device_count    INT DEFAULT 0,
    remark          VARCHAR(500),
    parent_id       BIGINT REFERENCES device_group(id),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by      BIGINT,
    updated_by      BIGINT,
    deleted_at      TIMESTAMP WITH TIME ZONE,
    CONSTRAINT chk_device_group_no_self_parent CHECK (parent_id IS NULL OR parent_id != id)
);

CREATE INDEX idx_device_group_parent ON device_group(parent_id) WHERE deleted_at IS NULL;

CREATE TRIGGER trg_device_group_updated_at
BEFORE UPDATE ON device_group FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE device_group_membership (
    device_group_id BIGINT NOT NULL REFERENCES device_group(id),
    device_id       BIGINT NOT NULL REFERENCES device(id),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (device_group_id, device_id)
);

-- --------------------------------------------------------------
-- 5. 算法与事件域
-- --------------------------------------------------------------

CREATE TABLE algorithm (
    id                  BIGSERIAL PRIMARY KEY,
    name                VARCHAR(100) NOT NULL,
    type                VARCHAR(50),
    description         VARCHAR(500),
    business_category   VARCHAR(50),
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by          BIGINT,
    updated_by          BIGINT,
    deleted_at          TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_algorithm_category ON algorithm(business_category) WHERE deleted_at IS NULL;

CREATE TRIGGER trg_algorithm_updated_at
BEFORE UPDATE ON algorithm FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE event_type (
    id              BIGSERIAL PRIMARY KEY,
    algorithm_id    BIGINT REFERENCES algorithm(id),
    name            VARCHAR(100) NOT NULL,
    description     VARCHAR(500),
    category        VARCHAR(20) DEFAULT 'detection',
    severity        INT DEFAULT 1,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by      BIGINT,
    updated_by      BIGINT,
    deleted_at      TIMESTAMP WITH TIME ZONE,
    CONSTRAINT chk_event_category CHECK (category IN ('detection', 'count', 'quality', 'traffic'))
);

CREATE INDEX idx_event_type_algorithm ON event_type(algorithm_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_event_type_category  ON event_type(category)     WHERE deleted_at IS NULL;

CREATE TRIGGER trg_event_type_updated_at
BEFORE UPDATE ON event_type FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE algorithm_service (
    id              BIGSERIAL PRIMARY KEY,
    service_id      VARCHAR(50),
    service_name    VARCHAR(100),
    service_code    VARCHAR(50),
    service_ip      INET,
    service_port    INT,
    annotation_ip   INET,
    annotation_port INT,
    status          VARCHAR(20) DEFAULT 'active',
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by      BIGINT,
    updated_by      BIGINT,
    deleted_at      TIMESTAMP WITH TIME ZONE,
    CONSTRAINT chk_algo_service_status CHECK (status IN ('active', 'inactive'))
);

CREATE TRIGGER trg_algorithm_service_updated_at
BEFORE UPDATE ON algorithm_service FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- --------------------------------------------------------------
-- 6. 业务运行域
-- --------------------------------------------------------------

CREATE TABLE deployment (
    id              BIGSERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    algorithm_id    BIGINT REFERENCES algorithm(id),
    service_id      BIGINT REFERENCES algorithm_service(id),
    status          VARCHAR(20) DEFAULT 'active',
    algorithm_status VARCHAR(20) DEFAULT 'running',
    deployed_at     TIMESTAMP WITH TIME ZONE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by      BIGINT,
    updated_by      BIGINT,
    deleted_at      TIMESTAMP WITH TIME ZONE,
    CONSTRAINT chk_deployment_status CHECK (status IN ('active', 'inactive')),
    CONSTRAINT chk_deployment_algo_status CHECK (algorithm_status IN ('running', 'stopped', 'error'))
);

CREATE INDEX idx_deployment_algorithm ON deployment(algorithm_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_deployment_service    ON deployment(service_id)    WHERE deleted_at IS NULL;

CREATE TRIGGER trg_deployment_updated_at
BEFORE UPDATE ON deployment FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE deployment_device (
    deployment_id   BIGINT NOT NULL REFERENCES deployment(id),
    device_id       BIGINT NOT NULL REFERENCES device(id),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (deployment_id, device_id)
);

CREATE TABLE deployment_schedule (
    id              BIGSERIAL PRIMARY KEY,
    deployment_id   BIGINT NOT NULL REFERENCES deployment(id) ON DELETE CASCADE,
    day_of_week     INT NOT NULL,
    start_time      TIME NOT NULL,
    end_time        TIME NOT NULL,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by      BIGINT,
    updated_by      BIGINT,
    CONSTRAINT chk_schedule_day CHECK (day_of_week BETWEEN 0 AND 6),
    CONSTRAINT chk_schedule_time CHECK (start_time < end_time)
);

CREATE INDEX idx_deployment_schedule_deployment ON deployment_schedule(deployment_id);

CREATE TRIGGER trg_deployment_schedule_updated_at
BEFORE UPDATE ON deployment_schedule FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE warning_event (
    id              BIGSERIAL PRIMARY KEY,
    device_id       BIGINT REFERENCES device(id),
    org_id          BIGINT REFERENCES organization(id),
    region_id       BIGINT REFERENCES region(id),
    algorithm_id    BIGINT REFERENCES algorithm(id),
    event_type_id   BIGINT REFERENCES event_type(id),
    rule_id         BIGINT REFERENCES linkage_rule(id),
    event_detail    VARCHAR(1000),
    process_status  VARCHAR(20) DEFAULT 'pending',
    is_compliant    BOOLEAN,
    report_time     TIMESTAMP WITH TIME ZONE,
    image_url       VARCHAR(500),
    video_url       VARCHAR(500),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by      BIGINT,
    CONSTRAINT chk_warning_status CHECK (process_status IN ('pending', 'processing', 'processed', 'ignored'))
);

CREATE INDEX idx_warning_device         ON warning_event(device_id);
CREATE INDEX idx_warning_org            ON warning_event(org_id);
CREATE INDEX idx_warning_region         ON warning_event(region_id);
CREATE INDEX idx_warning_event_type     ON warning_event(event_type_id);
CREATE INDEX idx_warning_rule           ON warning_event(rule_id);
CREATE INDEX idx_warning_report_time    ON warning_event(report_time);
CREATE INDEX idx_warning_process_status ON warning_event(process_status);

CREATE TRIGGER trg_warning_event_updated_at
BEFORE UPDATE ON warning_event FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- linkage_rule 必须在 warning_event 之后？不，warning_event FK 引用了 linkage_rule，所以 linkage_rule 要先创建
-- 修正：上面 warning_event 的 rule_id FK 指向 linkage_rule(id)，但 linkage_rule 还没创建
-- 改为先创建 linkage_rule

CREATE TABLE linkage_rule (
    id                  BIGSERIAL PRIMARY KEY,
    rule_name           VARCHAR(100) NOT NULL,
    trigger_mode        VARCHAR(20) DEFAULT 'AUTO',
    algorithm_id        BIGINT REFERENCES algorithm(id),
    event_type_id       BIGINT REFERENCES event_type(id),
    level               INT DEFAULT 1,
    delay_push          INT DEFAULT 0,
    is_compliant        VARCHAR(20),
    unit                VARCHAR(100),
    action_type         VARCHAR(50),
    status              VARCHAR(20) DEFAULT 'active',
    link                VARCHAR(500),
    content             TEXT,
    importance_level    INT DEFAULT 1,
    send_frequency      VARCHAR(50),
    push_channels       JSONB,
    app_id              VARCHAR(100),
    app_secret          VARCHAR(255),
    template_id         VARCHAR(100),
    push_target         VARCHAR(200),
    remark              VARCHAR(500),
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by          BIGINT,
    updated_by          BIGINT,
    deleted_at          TIMESTAMP WITH TIME ZONE,
    CONSTRAINT chk_linkage_trigger_mode CHECK (trigger_mode IN ('AUTO', 'MANUAL')),
    CONSTRAINT chk_linkage_status CHECK (status IN ('active', 'inactive'))
);

CREATE INDEX idx_linkage_algorithm   ON linkage_rule(algorithm_id)   WHERE deleted_at IS NULL;
CREATE INDEX idx_linkage_event_type  ON linkage_rule(event_type_id)  WHERE deleted_at IS NULL;
CREATE INDEX idx_linkage_trigger_mode ON linkage_rule(trigger_mode)  WHERE deleted_at IS NULL;
CREATE INDEX idx_linkage_status      ON linkage_rule(status)        WHERE deleted_at IS NULL;

CREATE TRIGGER trg_linkage_rule_updated_at
BEFORE UPDATE ON linkage_rule FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 补充 warning_event 的 rule_id 外键
ALTER TABLE warning_event ADD CONSTRAINT fk_warning_rule
    FOREIGN KEY (rule_id) REFERENCES linkage_rule(id);

CREATE TABLE linkage_rule_device (
    linkage_rule_id BIGINT NOT NULL REFERENCES linkage_rule(id),
    device_id       BIGINT NOT NULL REFERENCES device(id),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (linkage_rule_id, device_id)
);

CREATE TABLE push_history (
    id              BIGSERIAL PRIMARY KEY,
    rule_id         BIGINT REFERENCES linkage_rule(id),
    device_id       BIGINT REFERENCES device(id),
    event_type_id   BIGINT REFERENCES event_type(id),
    push_channels   JSONB,
    push_target     VARCHAR(200),
    push_time       TIMESTAMP WITH TIME ZONE,
    status          VARCHAR(20),
    retry_count     INT DEFAULT 0,
    operator        VARCHAR(50),
    count           INT DEFAULT 1,
    detail          TEXT,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_push_history_rule   ON push_history(rule_id);
CREATE INDEX idx_push_history_device ON push_history(device_id);
CREATE INDEX idx_push_history_time   ON push_history(push_time);
CREATE INDEX idx_push_history_status ON push_history(status);

CREATE TABLE task (
    id              BIGSERIAL PRIMARY KEY,
    task_name       VARCHAR(100) NOT NULL,
    trigger_type    VARCHAR(20) DEFAULT 'cron',
    trigger_rule    VARCHAR(100),
    algorithm_id    BIGINT REFERENCES algorithm(id),
    status          VARCHAR(20) DEFAULT 'active',
    last_run_time   TIMESTAMP WITH TIME ZONE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by      BIGINT,
    updated_by      BIGINT,
    deleted_at      TIMESTAMP WITH TIME ZONE,
    CONSTRAINT chk_task_trigger_type CHECK (trigger_type IN ('cron', 'event')),
    CONSTRAINT chk_task_status CHECK (status IN ('active', 'inactive'))
);

CREATE INDEX idx_task_algorithm ON task(algorithm_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_task_status     ON task(status)      WHERE deleted_at IS NULL;

CREATE TRIGGER trg_task_updated_at
BEFORE UPDATE ON task FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE task_device (
    task_id     BIGINT NOT NULL REFERENCES task(id),
    device_id   BIGINT NOT NULL REFERENCES device(id),
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (task_id, device_id)
);

-- --------------------------------------------------------------
-- 7. 系统配置域
-- --------------------------------------------------------------

CREATE TABLE video_setting (
    id                      BIGSERIAL PRIMARY KEY,
    device_id               BIGINT NOT NULL REFERENCES device(id),
    event_types             JSONB DEFAULT '[]',
    record_duration_seconds INT DEFAULT 10,
    status                  BOOLEAN DEFAULT true,
    created_at              TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at              TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by              BIGINT,
    updated_by              BIGINT,
    deleted_at              TIMESTAMP WITH TIME ZONE,
    CONSTRAINT chk_video_duration CHECK (record_duration_seconds BETWEEN 6 AND 30),
    CONSTRAINT uq_video_setting_device UNIQUE (device_id)
);

CREATE INDEX idx_video_setting_device  ON video_setting(device_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_video_setting_status  ON video_setting(status)    WHERE deleted_at IS NULL;

CREATE TRIGGER trg_video_setting_updated_at
BEFORE UPDATE ON video_setting FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE file (
    id                  BIGSERIAL PRIMARY KEY,
    file_name           VARCHAR(255) NOT NULL,
    file_size_bytes     BIGINT,
    duration_seconds    INT,
    device_id           BIGINT REFERENCES device(id),
    file_type           VARCHAR(20),
    storage_path        VARCHAR(500),
    url                 VARCHAR(500),
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by          BIGINT,
    updated_by          BIGINT,
    deleted_at          TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_file_device ON file(device_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_file_type   ON file(file_type) WHERE deleted_at IS NULL;

CREATE TRIGGER trg_file_updated_at
BEFORE UPDATE ON file FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE dispose_tag (
    id              BIGSERIAL PRIMARY KEY,
    tag_name        VARCHAR(50) NOT NULL,
    tag_color       VARCHAR(20),
    usage_count     INT DEFAULT 0,
    remark          VARCHAR(500),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by      BIGINT,
    updated_by      BIGINT,
    deleted_at      TIMESTAMP WITH TIME ZONE
);

CREATE TRIGGER trg_dispose_tag_updated_at
BEFORE UPDATE ON dispose_tag FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE warning_event_tag (
    warning_event_id    BIGINT NOT NULL REFERENCES warning_event(id),
    dispose_tag_id      BIGINT NOT NULL REFERENCES dispose_tag(id),
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (warning_event_id, dispose_tag_id)
);

CREATE TABLE license (
    id              BIGSERIAL PRIMARY KEY,
    license_key     VARCHAR(255) NOT NULL,
    type            VARCHAR(50),
    device_limit    INT DEFAULT 0,
    used_count      INT DEFAULT 0,
    expire_date     DATE,
    status          VARCHAR(20) DEFAULT 'active',
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by      BIGINT,
    updated_by      BIGINT,
    deleted_at      TIMESTAMP WITH TIME ZONE
);

CREATE TRIGGER trg_license_updated_at
BEFORE UPDATE ON license FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE firmware (
    id                  BIGSERIAL PRIMARY KEY,
    name                VARCHAR(100),
    version             VARCHAR(50) NOT NULL,
    applicable_version  VARCHAR(50),
    force_upgrade       BOOLEAN DEFAULT false,
    description         TEXT,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by          BIGINT,
    updated_by          BIGINT,
    deleted_at          TIMESTAMP WITH TIME ZONE
);

CREATE TRIGGER trg_firmware_updated_at
BEFORE UPDATE ON firmware FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE operation_log (
    id              BIGSERIAL PRIMARY KEY,
    username        VARCHAR(50),
    action          VARCHAR(200),
    ip              INET,
    result          VARCHAR(20),
    module          VARCHAR(50),
    action_time     TIMESTAMP WITH TIME ZONE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_operation_log_user   ON operation_log(username);
CREATE INDEX idx_operation_log_module ON operation_log(module);
CREATE INDEX idx_operation_log_time   ON operation_log(action_time);

CREATE TABLE clean_record (
    id              BIGSERIAL PRIMARY KEY,
    type            VARCHAR(50),
    cutoff_time     TIMESTAMP WITH TIME ZONE,
    status          VARCHAR(20) DEFAULT 'pending',
    progress        DECIMAL(5, 2) DEFAULT 0,
    clean_size_bytes BIGINT DEFAULT 0,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by      BIGINT
);

CREATE INDEX idx_clean_record_status ON clean_record(status);
CREATE INDEX idx_clean_record_type   ON clean_record(type);

CREATE TABLE popup_setting (
    id              BIGSERIAL PRIMARY KEY,
    config_json     JSONB DEFAULT '{}',
    is_active       BOOLEAN DEFAULT true,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by      BIGINT,
    updated_by      BIGINT,
    deleted_at      TIMESTAMP WITH TIME ZONE
);

CREATE TRIGGER trg_popup_setting_updated_at
BEFORE UPDATE ON popup_setting FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE popup_event_limit (
    id                      BIGSERIAL PRIMARY KEY,
    device_id               BIGINT REFERENCES device(id),
    time_interval_seconds   INT DEFAULT 0,
    response_mode           VARCHAR(20) DEFAULT 'immediate',
    enabled                 BOOLEAN DEFAULT true,
    created_at              TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at              TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by              BIGINT,
    updated_by              BIGINT,
    deleted_at              TIMESTAMP WITH TIME ZONE,
    CONSTRAINT chk_popup_response_mode CHECK (response_mode IN ('immediate', 'silent', 'delayed'))
);

CREATE INDEX idx_popup_event_limit_device ON popup_event_limit(device_id) WHERE deleted_at IS NULL;

CREATE TRIGGER trg_popup_event_limit_updated_at
BEFORE UPDATE ON popup_event_limit FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE ui_theme (
    id              BIGSERIAL PRIMARY KEY,
    name            VARCHAR(50) NOT NULL,
    platform        VARCHAR(50),
    theme_color     VARCHAR(20),
    logo_url        VARCHAR(500),
    is_active       BOOLEAN DEFAULT false,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by      BIGINT,
    updated_by      BIGINT,
    deleted_at      TIMESTAMP WITH TIME ZONE
);

CREATE TRIGGER trg_ui_theme_updated_at
BEFORE UPDATE ON ui_theme FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE microservice (
    id              BIGSERIAL PRIMARY KEY,
    name            VARCHAR(100),
    service_name    VARCHAR(100),
    ip              INET,
    port            INT,
    status          VARCHAR(20) DEFAULT 'active',
    cpu_usage       DECIMAL(5, 2),
    memory_usage    DECIMAL(5, 2),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by      BIGINT,
    updated_by      BIGINT,
    deleted_at      TIMESTAMP WITH TIME ZONE
);

CREATE TRIGGER trg_microservice_updated_at
BEFORE UPDATE ON microservice FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- --------------------------------------------------------------
-- 8. 接入协议域
-- --------------------------------------------------------------

CREATE TABLE access_platform (
    id              BIGSERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    type            VARCHAR(20) NOT NULL,
    version         VARCHAR(50),
    device_count    INT DEFAULT 0,
    status          VARCHAR(20) DEFAULT 'active',
    config_json     JSONB DEFAULT '{}',
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by      BIGINT,
    updated_by      BIGINT,
    deleted_at      TIMESTAMP WITH TIME ZONE,
    CONSTRAINT chk_platform_type CHECK (type IN ('GB28181', 'ONVIF', 'RTSP', 'RTMP'))
);

CREATE TRIGGER trg_access_platform_updated_at
BEFORE UPDATE ON access_platform FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE gb28181_device (
    id              BIGSERIAL PRIMARY KEY,
    device_id       BIGINT NOT NULL REFERENCES device(id),
    manufacturer    VARCHAR(100),
    model           VARCHAR(100),
    sip_server_id   VARCHAR(50),
    sip_device_id   VARCHAR(50),
    status          VARCHAR(20) DEFAULT 'active',
    channels_json   JSONB DEFAULT '[]',
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by      BIGINT,
    updated_by      BIGINT,
    deleted_at      TIMESTAMP WITH TIME ZONE
);

CREATE UNIQUE INDEX uq_gb28181_device ON gb28181_device(device_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_gb28181_device_device ON gb28181_device(device_id) WHERE deleted_at IS NULL;

CREATE TRIGGER trg_gb28181_device_updated_at
BEFORE UPDATE ON gb28181_device FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE onvif_device (
    id              BIGSERIAL PRIMARY KEY,
    device_id       BIGINT NOT NULL REFERENCES device(id),
    manufacturer    VARCHAR(100),
    model           VARCHAR(100),
    ip              INET,
    port            INT,
    status          VARCHAR(20) DEFAULT 'active',
    profiles_json   JSONB DEFAULT '[]',
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by      BIGINT,
    updated_by      BIGINT,
    deleted_at      TIMESTAMP WITH TIME ZONE
);

CREATE UNIQUE INDEX uq_onvif_device ON onvif_device(device_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_onvif_device_device ON onvif_device(device_id) WHERE deleted_at IS NULL;

CREATE TRIGGER trg_onvif_device_updated_at
BEFORE UPDATE ON onvif_device FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- --------------------------------------------------------------
-- 9. 视频标注域
-- --------------------------------------------------------------

CREATE TABLE annotation (
    id              BIGSERIAL PRIMARY KEY,
    deployment_id   BIGINT REFERENCES deployment(id),
    device_id       BIGINT REFERENCES device(id),
    name            VARCHAR(100),
    type            VARCHAR(20) DEFAULT 'monitoring',
    polygon_json    JSONB NOT NULL DEFAULT '[]',
    color           VARCHAR(20),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by      BIGINT,
    updated_by      BIGINT,
    deleted_at      TIMESTAMP WITH TIME ZONE,
    CONSTRAINT chk_annotation_type CHECK (type IN ('monitoring', 'forbidden'))
);

CREATE INDEX idx_annotation_deployment ON annotation(deployment_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_annotation_device     ON annotation(device_id)     WHERE deleted_at IS NULL;
CREATE INDEX idx_annotation_type       ON annotation(type)          WHERE deleted_at IS NULL;

CREATE TRIGGER trg_annotation_updated_at
BEFORE UPDATE ON annotation FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE preset (
    id              BIGSERIAL PRIMARY KEY,
    device_id       BIGINT NOT NULL REFERENCES device(id),
    name            VARCHAR(100) NOT NULL,
    code            VARCHAR(20),
    p               DECIMAL(8, 2),
    t               DECIMAL(8, 2),
    z               DECIMAL(8, 2),
    time_range_json JSONB,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by      BIGINT,
    updated_by      BIGINT,
    deleted_at      TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_preset_device ON preset(device_id) WHERE deleted_at IS NULL;

CREATE TRIGGER trg_preset_updated_at
BEFORE UPDATE ON preset FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- --------------------------------------------------------------
-- 10. 归档表
-- --------------------------------------------------------------

CREATE TABLE warning_event_archive (
    LIKE warning_event INCLUDING ALL,
    archived_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE warning_event_archive DROP CONSTRAINT IF EXISTS warning_event_archive_rule_id_fkey;
