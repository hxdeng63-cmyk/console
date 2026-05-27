import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import AsyncSessionLocal
from app.models.organization import Organization
from app.models.user import User

# Pre-generated bcrypt hash for "123456"
DEFAULT_PASSWORD_HASH = "$2b$12$iD9EsjQj7UCB.R.C6m1GXOSmq3ZWHDvWzPl6J/1PQxnWo/Vqb0s2W"

async def seed_users_orgs():
    async with AsyncSessionLocal() as db:
        # Check organizations
        org_count_result = await db.execute(select(func.count()).select_from(Organization).where(Organization.deleted_at.is_(None)))
        org_count = org_count_result.scalar()

        # Check users
        user_count_result = await db.execute(select(func.count()).select_from(User).where(User.deleted_at.is_(None)))
        user_count = user_count_result.scalar()

        if org_count > 0 and user_count > 0:
            print(f"Organization table has {org_count} records, User table has {user_count} records, skipping seed.")
            return

        now = datetime.utcnow()

        # Create company (level=1)
        company = Organization(
            name="智慧交通科技有限公司",
            parent_id=None,
            level=1,
            sort=1,
            code="ROOT",
            remark="总部",
            created_at=now,
            updated_at=now
        )
        db.add(company)
        await db.flush()  # Get company.id

        # Create departments (level=2)
        depts_data = [
            ("研发部", 1, "DEV"),
            ("市场部", 2, "MKT"),
            ("运维部", 3, "OPS"),
            ("人事部", 4, "HR"),
        ]

        dept_objs = []
        for name, sort, code in depts_data:
            dept = Organization(
                name=name,
                parent_id=company.id,
                level=2,
                sort=sort,
                code=code,
                remark=name,
                created_at=now,
                updated_at=now
            )
            db.add(dept)
            dept_objs.append(dept)

        await db.flush()  # Get dept ids

        # Map dept name to id
        dept_map = {d.name: d.id for d in dept_objs}

        # Create users
        users_data = [
            ("zhangsan", "张三", "EMP001", "13800138001", "active", "admin", "研发部"),
            ("lisi", "李四", "EMP002", "13800138002", "active", "user", "研发部"),
            ("wangwu", "王五", "EMP003", "13800138003", "active", "user", "市场部"),
            ("zhaoliu", "赵六", "EMP004", "13800138004", "active", "user", "运维部"),
            ("sunqi", "孙七", "EMP005", "13800138005", "inactive", "guest", "人事部"),
        ]

        for username, real_name, employee_id, phone, status, role, dept_name in users_data:
            db.add(User(
                username=username,
                real_name=real_name,
                employee_id=employee_id,
                password=DEFAULT_PASSWORD_HASH,
                phone=phone,
                org_id=dept_map.get(dept_name),
                status=status,
                role=role,
                created_at=now,
                updated_at=now
            ))

        await db.commit()
        print(f"Inserted 1 company, {len(dept_objs)} departments, {len(users_data)} users.")


if __name__ == "__main__":
    asyncio.run(seed_users_orgs())
