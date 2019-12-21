import django_rq

from django.db import models
from django.conf import settings
from django.contrib.sessions.models import Session
from django.contrib.auth.signals import user_logged_in, user_logged_out

from ipware import get_client_ip

from KlimaKar.functions import report_user_login


class SingletonModel(models.Model):

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class UserSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE)
    client_ip = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name='Adres IP'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Czas zalogowania')

    class Meta:
        verbose_name = 'Sesja użytkownika'
        verbose_name_plural = 'Sesje użytkownika'

    def __str__(self):
        return '{}: {} ({})'.format(
            self.user,
            self.client_ip,
            self.created.date())

    def delete(self, *args, **kwargs):
        self.session.delete()
        return super().delete(*args, **kwargs)

    @staticmethod
    def user_logged_in_handler(sender, request, user, **kwargs):
        user_session = UserSession.objects.get_or_create(
            user=user,
            session_id=request.session.session_key)[0]
        user_session.client_ip = get_client_ip(request)[0]
        user_session.save()

        django_rq.enqueue(report_user_login, user_session)


    @staticmethod
    def user_logged_out_handler(sender, request, user, **kwargs):
        try:
            user_session = UserSession.objects.get(
                session_id=request.session.session_key)
            user_session.session.delete()
        except UserSession.DoesNotExist:
            pass

    @staticmethod
    def delete_user_sessions(user):
        user_sessions = UserSession.objects.filter(user=user)
        for user_session in user_sessions:
            user_session.session.delete()


user_logged_in.connect(UserSession.user_logged_in_handler)
user_logged_out.connect(UserSession.user_logged_out_handler)
