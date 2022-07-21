# Generated by Django 3.2.8 on 2022-07-18 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0004_pairs'),
    ]

    operations = [
        migrations.CreateModel(
            name='balances',
            fields=[
                ('id', models.TextField(db_column='sender', primary_key=True, serialize=False)),
                ('eth', models.FloatField(blank=True, db_column='eth', null=True)),
                ('crv', models.FloatField(blank=True, db_column='crv', null=True)),
                ('usdc', models.FloatField(blank=True, db_column='usdc', null=True)),
            ],
            options={
                'db_table': 'balances',
            },
        ),
    ]
