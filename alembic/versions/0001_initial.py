from alembic import op
import sqlalchemy as sa
revision="0001_initial"; down_revision=None; branch_labels=None; depends_on=None
def upgrade():
    op.create_table("organizations",sa.Column("id",sa.String(40),primary_key=True),sa.Column("name",sa.String(200),nullable=False),sa.Column("org_type",sa.String(80),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False))
    op.create_table("users",sa.Column("id",sa.String(40),primary_key=True),sa.Column("organization_id",sa.String(40),sa.ForeignKey("organizations.id"),nullable=False),sa.Column("name",sa.String(200),nullable=False),sa.Column("role",sa.String(50),nullable=False),sa.Column("active",sa.Boolean(),nullable=False,server_default=sa.true()),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False))
    op.create_index("ix_users_organization_id","users",["organization_id"])
    op.create_table("lots",sa.Column("id",sa.String(40),primary_key=True),sa.Column("producer_id",sa.String(100),nullable=False),sa.Column("product",sa.String(200),nullable=False),sa.Column("species",sa.String(200)),sa.Column("quantity_kg",sa.Float(),nullable=False),sa.Column("origin_state",sa.String(100),nullable=False),sa.Column("origin_district",sa.String(100),nullable=False),sa.Column("source_type",sa.String(100),nullable=False),sa.Column("evidence_status",sa.String(50),nullable=False),sa.Column("regulatory_status",sa.String(50),nullable=False),sa.Column("status",sa.String(50),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False))
    for n,c in [("ix_lots_producer_id","producer_id"),("ix_lots_origin_state","origin_state"),("ix_lots_origin_district","origin_district"),("ix_lots_status","status")]: op.create_index(n,"lots",[c])
    op.create_table("audit_events",sa.Column("id",sa.String(40),primary_key=True),sa.Column("entity_id",sa.String(40),nullable=False),sa.Column("action",sa.String(100),nullable=False),sa.Column("actor",sa.String(100),nullable=False),sa.Column("data",sa.JSON(),nullable=False),sa.Column("occurred_at",sa.DateTime(timezone=True),nullable=False))
    op.create_index("ix_audit_events_entity_id","audit_events",["entity_id"])
    op.create_table("lot_transitions",sa.Column("id",sa.String(40),primary_key=True),sa.Column("lot_id",sa.String(40),sa.ForeignKey("lots.id"),nullable=False),sa.Column("from_status",sa.String(50),nullable=False),sa.Column("to_status",sa.String(50),nullable=False),sa.Column("actor",sa.String(100),nullable=False),sa.Column("reason",sa.String(500),nullable=False),sa.Column("occurred_at",sa.DateTime(timezone=True),nullable=False))
    op.create_index("ix_lot_transitions_lot_id","lot_transitions",["lot_id"])
    op.create_table("evidence",sa.Column("id",sa.String(40),primary_key=True),sa.Column("entity_id",sa.String(40),nullable=False),sa.Column("evidence_type",sa.String(50),nullable=False),sa.Column("status",sa.String(50),nullable=False),sa.Column("source",sa.String(200),nullable=False),sa.Column("reference",sa.String(500),nullable=False),sa.Column("metadata_json",sa.JSON(),nullable=False),sa.Column("content_hash",sa.String(64),nullable=False),sa.Column("captured_at",sa.DateTime(timezone=True),nullable=False))
    op.create_index("ix_evidence_entity_id","evidence",["entity_id"])
def downgrade():
    for t in ["evidence","lot_transitions","audit_events","lots","users","organizations"]: op.drop_table(t)
