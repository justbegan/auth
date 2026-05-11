from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('user', '0004_alter_customuser_created_at_alter_customuser_id_and_more'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='customuser',
            index=models.Index(fields=['account_type', 'status'], name='user_customu_account_0e8216_idx'),
        ),
        migrations.AddIndex(
            model_name='customuser',
            index=models.Index(fields=['created_at'], name='user_customu_created_c2b5df_idx'),
        ),
        migrations.AddIndex(
            model_name='customuser',
            index=models.Index(fields=['email'], name='user_customu_email_4d2e10_idx'),
        ),
        migrations.AddIndex(
            model_name='customuser',
            index=models.Index(fields=['phone'], name='user_customu_phone_8f9794_idx'),
        ),
    ]
