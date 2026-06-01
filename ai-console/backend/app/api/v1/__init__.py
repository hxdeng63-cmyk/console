from fastapi import APIRouter

from app.api.v1.devices import router as devices_router
from app.api.v1.device_streams import router as device_streams_router
from app.api.v1.device_groups import router as device_groups_router
from app.api.v1.regions import router as regions_router
from app.api.v1.linkage_rules import router as linkage_rules_router, deployment_router
from app.api.v1.users import router as users_router
from app.api.v1.roles import router as roles_router
from app.api.v1.organizations import router as organizations_router
from app.api.v1.menus import router as menus_router
from app.api.v1.resources import router as resources_router
from app.api.v1 import algorithms
from app.api.v1 import event_types
from app.api.v1 import algorithm_services
from app.api.v1 import algorithm_events
from app.api.v1 import tasks
from app.api.v1 import annotations
from app.api.v1 import file_records
from app.api.v1 import firmware
from app.api.v1 import dispose_tags
from app.api.v1 import ui_themes
from app.api.v1 import popup_settings
from app.api.v1 import access_platforms
from app.api.v1.video_settings import router as video_settings_router
from app.api.v1.push_histories import router as push_histories_router
from app.api.v1.deployments import router as deployments_router
from app.api.v1.clean_records import router as clean_records_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.warning_events import router as warning_events_router
from app.api.v1.microservices import router as microservices_router
from app.api.v1.licenses import router as licenses_router
from app.api.v1.operation_logs import router as operation_logs_router
from app.api.v1.data_sources import router as data_sources_router
from app.api.v1.event_stats import router as event_stats_router
from app.api.v1.pt_weight_files import router as pt_weight_files_router
from app.api.v1.upload import router as upload_router

router = APIRouter()

router.include_router(devices_router)
router.include_router(device_streams_router)
router.include_router(device_groups_router)
router.include_router(regions_router)
router.include_router(linkage_rules_router)
router.include_router(deployment_router)
router.include_router(users_router)
router.include_router(roles_router)
router.include_router(organizations_router)
router.include_router(menus_router)
router.include_router(resources_router)
router.include_router(algorithms.router)
router.include_router(event_types.router)
router.include_router(algorithm_services.router)
router.include_router(algorithm_events.router)
router.include_router(tasks.router)
router.include_router(annotations.router)
router.include_router(file_records.router)
router.include_router(firmware.router)
router.include_router(dispose_tags.router)
router.include_router(ui_themes.router)
router.include_router(popup_settings.router)
router.include_router(access_platforms.router)
router.include_router(video_settings_router)
router.include_router(push_histories_router)
router.include_router(deployments_router)
router.include_router(clean_records_router)
router.include_router(dashboard_router)
router.include_router(warning_events_router)
router.include_router(microservices_router)
router.include_router(licenses_router)
router.include_router(operation_logs_router)
router.include_router(data_sources_router)
router.include_router(event_stats_router)
router.include_router(pt_weight_files_router)
router.include_router(upload_router)

__all__ = ["router"]