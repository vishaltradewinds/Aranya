from sqlalchemy import String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class OrganizationRecord(Base):
    __tablename__="organizations"
    id:Mapped[str]=mapped_column(String(40),primary_key=True)
    name:Mapped[str]=mapped_column(String(200),nullable=False)
    org_type:Mapped[str]=mapped_column(String(80),nullable=False)
    created_at:Mapped[DateTime]=mapped_column(DateTime(timezone=True),nullable=False)

class UserRecord(Base):
    __tablename__="users"
    id:Mapped[str]=mapped_column(String(40),primary_key=True)
    organization_id:Mapped[str]=mapped_column(ForeignKey("organizations.id"),nullable=False,index=True)
    name:Mapped[str]=mapped_column(String(200),nullable=False)
    role:Mapped[str]=mapped_column(String(50),nullable=False)
    active:Mapped[bool]=mapped_column(default=True,nullable=False)
    created_at:Mapped[DateTime]=mapped_column(DateTime(timezone=True),nullable=False)

class LotTransitionRecord(Base):
    __tablename__="lot_transitions"
    id:Mapped[str]=mapped_column(String(40),primary_key=True)
    lot_id:Mapped[str]=mapped_column(ForeignKey("lots.id"),nullable=False,index=True)
    from_status:Mapped[str]=mapped_column(String(50),nullable=False)
    to_status:Mapped[str]=mapped_column(String(50),nullable=False)
    actor:Mapped[str]=mapped_column(String(100),nullable=False)
    reason:Mapped[str]=mapped_column(String(500),nullable=False)
    occurred_at:Mapped[DateTime]=mapped_column(DateTime(timezone=True),nullable=False)
