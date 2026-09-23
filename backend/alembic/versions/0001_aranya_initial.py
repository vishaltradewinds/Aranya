from alembic import op
from app.db import Base

revision = "0001_aranya_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    Base.metadata.create_all(bind=op.get_bind())

def downgrade():
    # ARANYA production schema is append-only; destructive rollback is intentionally disabled.
    raise RuntimeError("Destructive production rollback is disabled.")
