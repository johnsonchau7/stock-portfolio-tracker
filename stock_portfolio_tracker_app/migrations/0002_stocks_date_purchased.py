# Generated by Django 2.2.10 on 2021-02-09 06:43

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('stock_portfolio_tracker_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stocks',
            name='date_purchased',
            field=models.CharField(default=django.utils.timezone.now, max_length=50),
            preserve_default=False,
        ),
    ]
