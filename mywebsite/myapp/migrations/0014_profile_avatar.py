from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0013_alter_book_cover_delete_hold"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="avatar",
            field=models.ImageField(upload_to="images/avatars/", null=True, blank=True),
        ),
    ]

