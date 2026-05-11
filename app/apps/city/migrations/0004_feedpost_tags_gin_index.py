import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('city', '0003_alter_airequest_city_alter_airequest_context_and_more'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='feedpost',
            index=django.contrib.postgres.indexes.GinIndex(fields=['tags'], name='city_feedpo_tags_390fb2_gin'),
        ),
    ]
