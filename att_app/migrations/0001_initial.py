# Generated by Django 2.0.1 on 2018-02-10 08:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Student_Attendance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.CharField(default='00/00/00', help_text='Enter the Date', max_length=15, verbose_name='Date')),
                ('in_time', models.CharField(default='00:00:00', help_text='Enter the IN Time', max_length=15, verbose_name='IN Time')),
                ('out_time', models.CharField(blank=True, help_text='Enter the OUT Time', max_length=15, null=True, verbose_name='OUT Time')),
                ('duration', models.CharField(blank=True, help_text='Enter the Duration', max_length=15, null=True, verbose_name='Duration')),
                ('status', models.CharField(default='0', help_text='Enter the Status', max_length=1, verbose_name='Student Status')),
                ('st_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Student_Details',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(help_text='Enter the First-Name', max_length=50, null=True, verbose_name='First Name')),
                ('last_name', models.CharField(help_text='Enter the Last Name', max_length=50, null=True, verbose_name='Last Name')),
                ('dob', models.DateField(help_text='Enter Date of Birth', max_length=8, null=True, verbose_name='Date of Birth')),
                ('address', models.CharField(help_text='Enter the Address', max_length=50, null=True, verbose_name='Address')),
                ('g_name', models.CharField(help_text='Enter the Student Guardian Name', max_length=50, null=True, verbose_name='Guardian Name')),
                ('phone', models.CharField(help_text='Enter Guardian Number', max_length=15, null=True, verbose_name='Guardian Phone')),
                ('st_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Teacher_Details',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(help_text='Enter the First-Name', max_length=50, null=True, verbose_name='First Name')),
                ('last_name', models.CharField(help_text='Enter the Last Name', max_length=50, null=True, verbose_name='Last Name')),
                ('dob', models.DateField(help_text='Enter Date of Birth', max_length=8, null=True, verbose_name='Date of Birth')),
                ('address', models.CharField(help_text='Enter the Address', max_length=50, null=True, verbose_name='Address')),
                ('phone', models.CharField(help_text='Enter Phone Number', max_length=15, null=True, verbose_name='Phone No')),
                ('t_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
