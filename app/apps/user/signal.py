# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.core.mail import send_mail
# import random
# from django.conf import settings

# from .models import VerificationCode
# from .models import CustomUser


# @receiver(post_save, sender=CustomUser)
# def create_verification_code(sender, instance, created, **kwargs):
#     if created:
#         code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
#         VerificationCode.objects.create(user=instance, code=code)
#         if 'testuser' not in instance.username:
#             send_mail(
#                 'Подтверждение регистрации',
#                 f'Ваш код подтверждения: {code}',
#                 settings.DEFAULT_FROM_EMAIL,
#                 [instance.email],
#                 fail_silently=False,
#             )
