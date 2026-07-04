"""Initial schema

Revision ID: 20260627_01
Revises: None
Create Date: 2026-06-27 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260627_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_roles_code"), "roles", ["code"], unique=True)

    op.create_table(
        "tenants",
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("deployment_mode", sa.String(length=40), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tenants_code"), "tenants", ["code"], unique=True)

    op.create_table(
        "sites",
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("timezone", sa.String(length=80), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sites_code"), "sites", ["code"], unique=False)
    op.create_index(op.f("ix_sites_tenant_id"), "sites", ["tenant_id"], unique=False)

    op.create_table(
        "users",
        sa.Column("tenant_id", sa.String(length=36), nullable=True),
        sa.Column("email", sa.String(length=160), nullable=False),
        sa.Column("full_name", sa.String(length=160), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_tenant_id"), "users", ["tenant_id"], unique=False)

    op.create_table(
        "user_role_assignments",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("role_id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_user_role_assignments_role_id"),
        "user_role_assignments",
        ["role_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_role_assignments_tenant_id"),
        "user_role_assignments",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_role_assignments_user_id"),
        "user_role_assignments",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "workbook_uploads",
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("site_id", sa.String(length=36), nullable=True),
        sa.Column("uploaded_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("original_file_name", sa.String(length=255), nullable=False),
        sa.Column("stored_file_path", sa.String(length=255), nullable=True),
        sa.Column("workbook_month", sa.String(length=20), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["site_id"], ["sites.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["uploaded_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_workbook_uploads_site_id"),
        "workbook_uploads",
        ["site_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_workbook_uploads_tenant_id"),
        "workbook_uploads",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_workbook_uploads_uploaded_by_user_id"),
        "workbook_uploads",
        ["uploaded_by_user_id"],
        unique=False,
    )

    op.create_table(
        "calculation_runs",
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("workbook_upload_id", sa.String(length=36), nullable=False),
        sa.Column("calculation_type", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["workbook_upload_id"], ["workbook_uploads.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_calculation_runs_tenant_id"),
        "calculation_runs",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_calculation_runs_workbook_upload_id"),
        "calculation_runs",
        ["workbook_upload_id"],
        unique=False,
    )

    op.create_table(
        "daily_consumption_records",
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("workbook_upload_id", sa.String(length=36), nullable=False),
        sa.Column("source_type", sa.String(length=40), nullable=False),
        sa.Column("reading_date", sa.Date(), nullable=False),
        sa.Column("metric_name", sa.String(length=60), nullable=False),
        sa.Column("category_code", sa.String(length=20), nullable=True),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["workbook_upload_id"], ["workbook_uploads.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_daily_consumption_records_reading_date"),
        "daily_consumption_records",
        ["reading_date"],
        unique=False,
    )
    op.create_index(
        op.f("ix_daily_consumption_records_tenant_id"),
        "daily_consumption_records",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_daily_consumption_records_workbook_upload_id"),
        "daily_consumption_records",
        ["workbook_upload_id"],
        unique=False,
    )

    op.create_table(
        "sheet_ingestions",
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("workbook_upload_id", sa.String(length=36), nullable=False),
        sa.Column("sheet_name", sa.String(length=120), nullable=False),
        sa.Column("sheet_type", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("row_count", sa.Integer(), nullable=True),
        sa.Column("validation_summary", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["workbook_upload_id"], ["workbook_uploads.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_sheet_ingestions_tenant_id"),
        "sheet_ingestions",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_sheet_ingestions_workbook_upload_id"),
        "sheet_ingestions",
        ["workbook_upload_id"],
        unique=False,
    )

    op.create_table(
        "solar_daily_records",
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("workbook_upload_id", sa.String(length=36), nullable=False),
        sa.Column("reading_date", sa.Date(), nullable=False),
        sa.Column("metric_name", sa.String(length=60), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["workbook_upload_id"], ["workbook_uploads.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_solar_daily_records_reading_date"),
        "solar_daily_records",
        ["reading_date"],
        unique=False,
    )
    op.create_index(
        op.f("ix_solar_daily_records_tenant_id"),
        "solar_daily_records",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_solar_daily_records_workbook_upload_id"),
        "solar_daily_records",
        ["workbook_upload_id"],
        unique=False,
    )

    op.create_table(
        "solar_working_results",
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("workbook_upload_id", sa.String(length=36), nullable=False),
        sa.Column("reading_date", sa.Date(), nullable=False),
        sa.Column("tneb_c1", sa.Float(), nullable=False),
        sa.Column("tneb_c2", sa.Float(), nullable=False),
        sa.Column("tneb_c4", sa.Float(), nullable=False),
        sa.Column("tneb_c5", sa.Float(), nullable=False),
        sa.Column("tneb_total", sa.Float(), nullable=False),
        sa.Column("iex_c1", sa.Float(), nullable=False),
        sa.Column("iex_c2", sa.Float(), nullable=False),
        sa.Column("iex_c4", sa.Float(), nullable=False),
        sa.Column("iex_c5", sa.Float(), nullable=False),
        sa.Column("iex_total", sa.Float(), nullable=False),
        sa.Column("post_iex_balance", sa.Float(), nullable=False),
        sa.Column("solar_total", sa.Float(), nullable=False),
        sa.Column("tneb_balance", sa.Float(), nullable=False),
        sa.Column("banking_balance", sa.Float(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["workbook_upload_id"], ["workbook_uploads.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_solar_working_results_reading_date"),
        "solar_working_results",
        ["reading_date"],
        unique=False,
    )
    op.create_index(
        op.f("ix_solar_working_results_tenant_id"),
        "solar_working_results",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_solar_working_results_workbook_upload_id"),
        "solar_working_results",
        ["workbook_upload_id"],
        unique=False,
    )

    op.create_table(
        "source_interval_records",
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("workbook_upload_id", sa.String(length=36), nullable=False),
        sa.Column("source_type", sa.String(length=40), nullable=False),
        sa.Column("reading_date", sa.Date(), nullable=False),
        sa.Column("time_block_label", sa.String(length=40), nullable=False),
        sa.Column("category_code", sa.String(length=20), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["workbook_upload_id"], ["workbook_uploads.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_source_interval_records_reading_date"),
        "source_interval_records",
        ["reading_date"],
        unique=False,
    )
    op.create_index(
        op.f("ix_source_interval_records_tenant_id"),
        "source_interval_records",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_source_interval_records_workbook_upload_id"),
        "source_interval_records",
        ["workbook_upload_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_source_interval_records_workbook_upload_id"), table_name="source_interval_records")
    op.drop_index(op.f("ix_source_interval_records_tenant_id"), table_name="source_interval_records")
    op.drop_index(op.f("ix_source_interval_records_reading_date"), table_name="source_interval_records")
    op.drop_table("source_interval_records")

    op.drop_index(op.f("ix_solar_working_results_workbook_upload_id"), table_name="solar_working_results")
    op.drop_index(op.f("ix_solar_working_results_tenant_id"), table_name="solar_working_results")
    op.drop_index(op.f("ix_solar_working_results_reading_date"), table_name="solar_working_results")
    op.drop_table("solar_working_results")

    op.drop_index(op.f("ix_solar_daily_records_workbook_upload_id"), table_name="solar_daily_records")
    op.drop_index(op.f("ix_solar_daily_records_tenant_id"), table_name="solar_daily_records")
    op.drop_index(op.f("ix_solar_daily_records_reading_date"), table_name="solar_daily_records")
    op.drop_table("solar_daily_records")

    op.drop_index(op.f("ix_sheet_ingestions_workbook_upload_id"), table_name="sheet_ingestions")
    op.drop_index(op.f("ix_sheet_ingestions_tenant_id"), table_name="sheet_ingestions")
    op.drop_table("sheet_ingestions")

    op.drop_index(op.f("ix_daily_consumption_records_workbook_upload_id"), table_name="daily_consumption_records")
    op.drop_index(op.f("ix_daily_consumption_records_tenant_id"), table_name="daily_consumption_records")
    op.drop_index(op.f("ix_daily_consumption_records_reading_date"), table_name="daily_consumption_records")
    op.drop_table("daily_consumption_records")

    op.drop_index(op.f("ix_calculation_runs_workbook_upload_id"), table_name="calculation_runs")
    op.drop_index(op.f("ix_calculation_runs_tenant_id"), table_name="calculation_runs")
    op.drop_table("calculation_runs")

    op.drop_index(op.f("ix_workbook_uploads_uploaded_by_user_id"), table_name="workbook_uploads")
    op.drop_index(op.f("ix_workbook_uploads_tenant_id"), table_name="workbook_uploads")
    op.drop_index(op.f("ix_workbook_uploads_site_id"), table_name="workbook_uploads")
    op.drop_table("workbook_uploads")

    op.drop_index(op.f("ix_user_role_assignments_user_id"), table_name="user_role_assignments")
    op.drop_index(op.f("ix_user_role_assignments_tenant_id"), table_name="user_role_assignments")
    op.drop_index(op.f("ix_user_role_assignments_role_id"), table_name="user_role_assignments")
    op.drop_table("user_role_assignments")

    op.drop_index(op.f("ix_users_tenant_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    op.drop_index(op.f("ix_sites_tenant_id"), table_name="sites")
    op.drop_index(op.f("ix_sites_code"), table_name="sites")
    op.drop_table("sites")

    op.drop_index(op.f("ix_tenants_code"), table_name="tenants")
    op.drop_table("tenants")

    op.drop_index(op.f("ix_roles_code"), table_name="roles")
    op.drop_table("roles")
