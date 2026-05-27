import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.ui_theme import UITheme


async def seed_ui_themes():
    async with AsyncSessionLocal() as db:
        count_result = await db.execute(
            select(func.count()).select_from(UITheme).where(UITheme.deleted_at.is_(None))
        )
        count = count_result.scalar()
        if count > 0:
            print(f"UITheme table already has {count} records, skipping seed.")
            return

        now = datetime.utcnow()

        themes = [
            UITheme(
                name="默认主题",
                platform="web",
                theme_color="#409EFF",
                logo_url="/logo-default.png",
                is_active=True,
                created_at=now,
                updated_at=now,
            ),
            UITheme(
                name="暗色主题",
                platform="web",
                theme_color="#303133",
                logo_url="/logo-dark.png",
                is_active=False,
                created_at=now,
                updated_at=now,
            ),
            UITheme(
                name="移动端主题",
                platform="mobile",
                theme_color="#67C23A",
                logo_url="/logo-mobile.png",
                is_active=False,
                created_at=now,
                updated_at=now,
            ),
        ]

        db.add_all(themes)
        await db.commit()
        print(f"UITheme seed completed! Inserted {len(themes)} themes.")


if __name__ == "__main__":
    asyncio.run(seed_ui_themes())
