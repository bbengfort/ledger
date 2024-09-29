# budget.management.commands.importsubscriptions
# Import subscriptions from a CSV on the command line.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sun Sep 29 15:28:17 2024 -0500
#
# Copyright (C) 2024 Bengfort.com
# For license information, see LICENSE
#
# ID: importsubscriptions.py [] benjamin@bengfort.com $

"""
Import subscriptions from a CSV on the command line.
"""

##########################################################################
## Imports
##########################################################################

import csv

from decimal import Decimal

from budget.models import Category, Subscription
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = "Import subscriptions from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv", nargs=1, help="the path of the csv file to import")

    def read_csv(self, path):
        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                for k, v in row.items():
                    if '$' in v:
                        v = v.replace('$', '')
                    row[k] = v.strip()
                yield row

    def handle(self, *args, **options):
        n = 0
        for row in self.read_csv(options['csv'][0]):
            category, _ = Category.objects.get_or_create(name=row["Category"])
            subscription = Subscription(
                name=row["Description"],
                notes=row['Notes'],
                amount=Decimal(row['Cost']),
                frequency=int(row['Frequency']),
                category=category,
                active=True,
                exclude=False,
                order=n+1,
            )

            subscription.save()
            n +=1

        self.stdout.write(
            self.style.SUCCESS(f"successfully imported {n} rows from the csv file")
        )
