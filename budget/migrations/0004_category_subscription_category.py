# Generated by Django 5.1.1 on 2024-09-29 20:17

import colorfield.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("budget", "0003_subscription_alter_budget_id_alter_budget_year_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
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
                (
                    "name",
                    models.CharField(
                        default=None,
                        help_text="Name of the category",
                        max_length=128,
                        unique=True,
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Any notes or other information about the category",
                    ),
                ),
                (
                    "color",
                    colorfield.fields.ColorField(
                        default="#CCCCCC",
                        help_text="The color to assign to the category in labels and bar charts",
                        image_field=None,
                        max_length=25,
                        samples=None,
                    ),
                ),
                (
                    "active",
                    models.BooleanField(
                        default=True,
                        help_text="Show the category in the active categories list",
                    ),
                ),
                (
                    "exclude",
                    models.BooleanField(
                        default=False,
                        help_text="Exclude any items from this category in overview and aggregations",
                    ),
                ),
            ],
            options={
                "verbose_name": "category",
                "verbose_name_plural": "categories",
                "db_table": "budget_categories",
                "ordering": ("name",),
            },
        ),
        migrations.AddField(
            model_name="subscription",
            name="category",
            field=models.ForeignKey(
                help_text="The category of this subscription for aggregation and tracking",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="subscriptions",
                to="budget.category",
            ),
        ),
    ]
