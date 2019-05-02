# Generated by Django 2.2.1 on 2019-05-02 02:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveSmallIntegerField(default=2019, help_text='Household fiscal year', unique=True)),
                ('description', models.TextField(blank=True, default='', help_text='Budget goals, notes, and general information')),
            ],
            options={
                'db_table': 'budgets',
                'ordering': ('-year',),
            },
        ),
        migrations.CreateModel(
            name='LineItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=None, help_text='Name of income or expense', max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, help_text='Projected amount per period', max_digits=10)),
                ('frequency', models.PositiveSmallIntegerField(default=12, help_text='Number of times per year amount is paid')),
                ('is_income', models.BooleanField(default=False, help_text='Check if income source, uncheck if expense')),
                ('notes', models.CharField(blank=True, default='', help_text='Notes or other details about line item', max_length=512)),
                ('order', models.PositiveSmallIntegerField(blank=True, default=None, help_text='User defined order for display', null=True)),
                ('budget', models.ForeignKey(help_text='the budget to assign this line item to', on_delete=django.db.models.deletion.CASCADE, related_name='line_items', to='budget.Budget')),
            ],
            options={
                'db_table': 'budget_line_items',
                'ordering': ('-budget__year', 'order'),
            },
        ),
    ]
