# Generated by Django 3.2.8 on 2022-07-21 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0009_auto_20220718_1415'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactions',
            name='matching_id',
            field=models.TextField(blank=True, db_column='matching_id', null=True),
        ),
    ]
