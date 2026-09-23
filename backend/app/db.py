from datetime import datetime, timezone
from sqlalchemy import create_engine, String, DateTime, Float, JSON, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
import os
DATABASE_URL=os.getenv("DATABASE_URL","sqlite:///./aranya.db")
engine_kwargs={}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"]={"check_same_thread":False}
else:
    engine_kwargs["pool_pre_ping"]=True
engine=create_engine(DATABASE_URL,**engine_kwargs)
SessionLocal=sessionmaker(bind=engine,autoflush=False,expire_on_commit=False)
class Base(DeclarativeBase): pass
class LotRecord(Base):
    __tablename__="lots"
    id:Mapped[str]=mapped_column(String(40),primary_key=True)
    producer_id:Mapped[str]=mapped_column(String(100),nullable=False,index=True)
    product:Mapped[str]=mapped_column(String(200),nullable=False)
    species:Mapped[str|None]=mapped_column(String(200))
    quantity_kg:Mapped[float]=mapped_column(Float,nullable=False)
    origin_state:Mapped[str]=mapped_column(String(100),nullable=False,index=True)
    origin_district:Mapped[str]=mapped_column(String(100),nullable=False,index=True)
    source_type:Mapped[str]=mapped_column(String(100),nullable=False)
    evidence_status:Mapped[str]=mapped_column(String(50),nullable=False)
    regulatory_status:Mapped[str]=mapped_column(String(50),nullable=False)
    status:Mapped[str]=mapped_column(String(50),nullable=False,index=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False)
class AuditRecord(Base):
    __tablename__="audit_events"
    id:Mapped[str]=mapped_column(String(40),primary_key=True)
    entity_id:Mapped[str]=mapped_column(String(40),nullable=False,index=True)
    action:Mapped[str]=mapped_column(String(100),nullable=False)
    actor:Mapped[str]=mapped_column(String(100),nullable=False)
    data:Mapped[dict]=mapped_column(JSON,nullable=False)
    occurred_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False)
class OrganizationRecord(Base):
    __tablename__="organizations"
    id:Mapped[str]=mapped_column(String(40),primary_key=True)
    name:Mapped[str]=mapped_column(String(200),nullable=False)
    org_type:Mapped[str]=mapped_column(String(80),nullable=False)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False)
class UserRecord(Base):
    __tablename__="users"
    id:Mapped[str]=mapped_column(String(40),primary_key=True)
    organization_id:Mapped[str]=mapped_column(ForeignKey("organizations.id"),nullable=False,index=True)
    name:Mapped[str]=mapped_column(String(200),nullable=False)
    role:Mapped[str]=mapped_column(String(50),nullable=False)
    active:Mapped[bool]=mapped_column(Boolean,default=True,nullable=False)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False)
class LotTransitionRecord(Base):
    __tablename__="lot_transitions"
    id:Mapped[str]=mapped_column(String(40),primary_key=True)
    lot_id:Mapped[str]=mapped_column(ForeignKey("lots.id"),nullable=False,index=True)
    from_status:Mapped[str]=mapped_column(String(50),nullable=False)
    to_status:Mapped[str]=mapped_column(String(50),nullable=False)
    actor:Mapped[str]=mapped_column(String(100),nullable=False)
    reason:Mapped[str]=mapped_column(String(500),nullable=False)
    occurred_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False)
class EvidenceRecord(Base):
    __tablename__="evidence"
    id:Mapped[str]=mapped_column(String(40),primary_key=True)
    entity_id:Mapped[str]=mapped_column(String(40),nullable=False,index=True)
    evidence_type:Mapped[str]=mapped_column(String(50),nullable=False)
    status:Mapped[str]=mapped_column(String(50),nullable=False)
    source:Mapped[str]=mapped_column(String(200),nullable=False)
    reference:Mapped[str]=mapped_column(String(500),nullable=False)
    metadata_json:Mapped[dict]=mapped_column(JSON,nullable=False)
    content_hash:Mapped[str]=mapped_column(String(64),nullable=False)
    captured_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False)

class NetworkRecord(Base):
    __tablename__="networks"
    id:Mapped[str]=mapped_column(String(40),primary_key=True)
    organization_id:Mapped[str|None]=mapped_column(ForeignKey("organizations.id"),nullable=True,index=True)
    name:Mapped[str]=mapped_column(String(200),nullable=False)
    network_type:Mapped[str]=mapped_column(String(80),nullable=False,index=True)
    description:Mapped[str|None]=mapped_column(String(1000))
    capabilities:Mapped[list]=mapped_column(JSON,nullable=False,default=list)
    needs:Mapped[list]=mapped_column(JSON,nullable=False,default=list)
    jurisdiction:Mapped[str|None]=mapped_column(String(200))
    active:Mapped[bool]=mapped_column(Boolean,default=True,nullable=False,index=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False)
class NetworkLinkRecord(Base):
    __tablename__="network_links"
    id:Mapped[str]=mapped_column(String(40),primary_key=True)
    source_network_id:Mapped[str]=mapped_column(ForeignKey("networks.id"),nullable=False,index=True)
    target_network_id:Mapped[str]=mapped_column(ForeignKey("networks.id"),nullable=False,index=True)
    relation:Mapped[str]=mapped_column(String(80),nullable=False)
    status:Mapped[str]=mapped_column(String(40),nullable=False)
    evidence_id:Mapped[str|None]=mapped_column(String(40))
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False)


class JourneyRecord(Base):
    __tablename__="journeys"
    id:Mapped[str]=mapped_column(String(40),primary_key=True)
    stakeholder_id:Mapped[str]=mapped_column(String(100),nullable=False,index=True)
    intent_type:Mapped[str]=mapped_column(String(50),nullable=False,index=True)
    journey_key:Mapped[str]=mapped_column(String(100),nullable=False,index=True)
    state:Mapped[str]=mapped_column(String(50),nullable=False,index=True)
    intent_payload:Mapped[dict]=mapped_column(JSON,nullable=False)
    next_action:Mapped[str]=mapped_column(String(200),nullable=False)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False)
    updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False)

def init_db(): Base.metadata.create_all(engine)