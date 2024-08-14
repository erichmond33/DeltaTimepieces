# Generated by Django 5.1 on 2024-08-14 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Watch",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("Name", models.CharField(max_length=500)),
                ("price", models.IntegerField()),
                ("year", models.IntegerField()),
                ("image", models.ImageField(upload_to="images/")),
            ],
        ),
    ]
