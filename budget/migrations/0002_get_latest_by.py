# Generated by Django 3.0.2 on 2020-02-04 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='budget',
            options={'get_latest_by': 'year', 'ordering': ('-year',)},
        ),
        migrations.AlterField(
            model_name='budget',
            name='year',
            field=models.PositiveSmallIntegerField(default=2020, help_text='Household fiscal year', unique=True),
        ),
    ]
