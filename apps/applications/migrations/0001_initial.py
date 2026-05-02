from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("jobs", "0002_application_applicant_company_owner_and_more"),
        ("accounts", "0003_alter_pendingregistration_user_type_and_more"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name="Application",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("full_name", models.CharField(max_length=180)),
                        ("email", models.EmailField(max_length=254)),
                        ("phone", models.CharField(blank=True, max_length=50)),
                        ("resume_url", models.URLField(blank=True)),
                        ("cover_letter", models.TextField(blank=True)),
                        (
                            "status",
                            models.CharField(
                                choices=[
                                    ("submitted", "Submitted"),
                                    ("reviewing", "Reviewing"),
                                    ("rejected", "Rejected"),
                                    ("hired", "Hired"),
                                ],
                                default="submitted",
                                max_length=20,
                            ),
                        ),
                        ("applied_at", models.DateTimeField(auto_now_add=True)),
                        ("updated_at", models.DateTimeField(auto_now=True)),
                        (
                            "applicant",
                            models.ForeignKey(
                                blank=True,
                                null=True,
                                on_delete=django.db.models.deletion.SET_NULL,
                                related_name="job_applications",
                                to="accounts.user",
                            ),
                        ),
                        (
                            "job",
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name="applications",
                                to="jobs.job",
                            ),
                        ),
                    ],
                    options={
                        "db_table": "jobs_application",
                        "ordering": ["-applied_at"],
                    },
                ),
                migrations.AddConstraint(
                    model_name="application",
                    constraint=models.UniqueConstraint(
                        fields=("job", "applicant"), name="unique_job_application_per_user"
                    ),
                ),
            ],
        )
    ]

