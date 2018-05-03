# Change the name of the tax return table

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('taxes', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='taxreturn',
            table='tax_returns',
        ),
    ]
