# Generated manually for API docs page image upload

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_apiendpoint_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='apidocumentationpage',
            name='image',
            field=models.ImageField(
                blank=True,
                help_text='Upload an image for this page (e.g. screenshot or mockup)',
                null=True,
                upload_to='api_docs/pages/',
            ),
        ),
    ]
