from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("applications", "0001_initial"),
        ("jobs", "0002_application_applicant_company_owner_and_more"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(name="Application"),
            ],
        )
    ]

