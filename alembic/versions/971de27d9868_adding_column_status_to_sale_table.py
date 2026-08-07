from alembic import op
import sqlalchemy as sa

revision = "971de27d9868"
down_revision = "d29cd81c937e"
branch_labels = None
depends_on = None


sale_status = sa.Enum(
    "PENDIENTE",
    "PARCIAL",
    "PAGADA",
    name="salestatus"
)


def upgrade():

    # Crear el tipo ENUM en PostgreSQL
    sale_status.create(op.get_bind(), checkfirst=True)

    # Agregar la columna
    op.add_column(
        "sale",
        sa.Column(
            "status",
            sale_status,
            nullable=False,
            server_default="PENDIENTE"
        )
    )

    # Opcional: eliminar el default después de poblar los registros existentes
    op.alter_column(
        "sale",
        "status",
        server_default=None
    )


def downgrade():

    op.drop_column("sale", "status")

    sale_status.drop(op.get_bind(), checkfirst=True)
