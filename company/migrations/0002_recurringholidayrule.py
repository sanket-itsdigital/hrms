# Generated manually for Recurring Holiday Rule (e.g. 2nd & 4th Saturday)

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0001_initial'),
        ('company', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecurringHolidayRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='e.g. 2nd Saturday Off', max_length=255)),
                ('weekday', models.PositiveSmallIntegerField(choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')])),
                ('week_of_month', models.PositiveSmallIntegerField(help_text='1=1st occurrence in month, 2=2nd, 3=3rd, 4=4th, 5=5th')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recurring_holiday_rules', to='organizations.organization')),
            ],
            options={
                'verbose_name': 'Recurring Holiday Rule',
                'verbose_name_plural': 'Recurring Holiday Rules',
                'db_table': 'recurring_holiday_rules',
                'ordering': ['weekday', 'week_of_month'],
                'unique_together': {('organization', 'weekday', 'week_of_month')},
            },
        ),
    ]
