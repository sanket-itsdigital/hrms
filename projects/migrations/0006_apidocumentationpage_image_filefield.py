# Change ImageField to FileField so uploads work without Pillow image validation

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0005_add_api_page_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apidocumentationpage',
            name='image',
            field=models.FileField(
                blank=True,
                help_text='Upload an image for this page (e.g. screenshot or mockup)',
                null=True,
                upload_to='api_docs/pages/',
            ),
        ),
    ]
