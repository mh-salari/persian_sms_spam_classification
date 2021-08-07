# Generated by Django 3.2.6 on 2021-08-07 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SMS',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(max_length=1000, unique=True)),
                ('label', models.CharField(choices=[('spam', 'Spam'), ('ham', 'Ham')], default='spam', max_length=25)),
            ],
        ),
    ]
