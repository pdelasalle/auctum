# Generated by Django 3.2.8 on 2022-07-15 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transactions',
            name='qty_buy',
        ),
        migrations.RemoveField(
            model_name='transactions',
            name='token_buy',
        ),
        migrations.RemoveField(
            model_name='transactions',
            name='token_sell',
        ),
        migrations.AddField(
            model_name='transactions',
            name='pair',
            field=models.TextField(blank=True, db_column='pair', null=True),
        ),
        migrations.AddField(
            model_name='transactions',
            name='qty_side',
            field=models.FloatField(blank=True, db_column='qty_side', null=True),
        ),
        migrations.AddField(
            model_name='transactions',
            name='side',
            field=models.TextField(blank=True, db_column='side', null=True),
        ),
    ]
