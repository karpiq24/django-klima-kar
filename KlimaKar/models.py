import os
import requests

from django.db import models
from django.core.mail import mail_admins

from KlimaKar import settings
from KlimaKar.functions import encode_media_related


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


class MyCloudHome(SingletonModel):
    APP_DIR_NAME = 'django-klima-kar'
    COMMISSION_DIR_NAME = 'commission'

    REFRESH_TOKEN = models.CharField(
        max_length=1024,
        blank=True,
        null=True)
    ACCESS_TOKEN = models.CharField(
        max_length=2048,
        blank=True,
        null=True)
    USER_ID = models.CharField(
        max_length=128,
        blank=True,
        null=True)
    DEVICE_ID = models.CharField(
        max_length=128,
        blank=True,
        null=True)
    DEVICE_NAME = models.CharField(
        max_length=256,
        blank=True,
        null=True)
    DEVICE_INTERNAL_URL = models.CharField(
        max_length=256,
        blank=True,
        null=True)
    DEVICE_EXTERNAL_URL = models.CharField(
        max_length=256,
        blank=True,
        null=True)
    APP_DIR_ID = models.CharField(
        max_length=128,
        blank=True,
        null=True)
    COMMISSION_DIR_ID = models.CharField(
        max_length=128,
        blank=True,
        null=True)

    def initialize(self):
        if not self.REFRESH_TOKEN:
            self.authorize_connection()
        if not self.ACCESS_TOKEN:
            self._refresh_token()
        if not self._check_access_token():
            self._refresh_token()
        if not self.USER_ID:
            self.get_user_info()
        if not self.DEVICE_ID or not self.DEVICE_NAME or not self.DEVICE_INTERNAL_URL or not self.DEVICE_EXTERNAL_URL:
            self.get_user_devices()
        if not self.APP_DIR_ID:
            r = self.create_folder(self.APP_DIR_NAME)
            if r.status_code == 201:
                self.APP_DIR_ID = r.headers['Location'].split('/')[-1]
                self.save()
            else:
                files = self.get_files()['files']
                for f in files:
                    if f['name'] == self.APP_DIR_NAME:
                        self.APP_DIR_ID = f['id']
                        self.save()
                        break
        if not self.COMMISSION_DIR_ID:
            r = self.create_folder(self.COMMISSION_DIR_NAME, self.APP_DIR_ID)
            if r.status_code == 201:
                self.COMMISSION_DIR_ID = r.headers['Location'].split('/')[-1]
                self.save()
            else:
                files = self.get_files(self.APP_DIR_ID)['files']
                for f in files:
                    if f['name'] == self.COMMISSION_DIR_NAME:
                        self.COMMISSION_DIR_ID = f['id']
                        self.save()
                        break

    def _get_endpoint(self, endpoint):
        url = 'http://config.mycloud.com/config/v1/config'
        r = requests.get(url)
        return r.json()['data']['componentMap']['cloud.service.urls'][endpoint]

    def _get_auth_url(self):
        url = os.path.join(self._get_endpoint('service.auth0.url'), 'authorize')
        params = {
            'scope': 'openid offline_access nas_read_write nas_read_only user_read device_read',
            'response_type': 'code',
            'connection': 'Username-Password-Authentication',
            'sso': 'false',
            'audience': 'mycloud.com',
            'state': 'my-custom-state',
            'protocol': 'oauth2',
            'redirect_uri': 'http://localhost',
            'client_id': settings.WD_CLIENT_ID
        }
        pr = requests.models.PreparedRequest()
        pr.prepare(method='get', url=url, params=params)
        return pr.url

    def _get_access_and_refresh_token(self, code):
        url = os.path.join(self._get_endpoint('service.auth0.url'), 'oauth', 'token')
        data = {
            'code': code,
            'audience': 'mycloud.com',
            'client_id': settings.WD_CLIENT_ID,
            'client_secret': settings.WD_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'redirect_uri': 'http://localhost'
        }
        r = requests.post(url, data=data)
        return r.json()

    def authorize_connection(self):
        print(self._get_auth_url())
        print('\nPodaj kod z URL:')
        code = input()
        data = self._get_access_and_refresh_token(code)
        self.ACCESS_TOKEN = data['access_token']
        self.REFRESH_TOKEN = data['refresh_token']
        self.save()

    def _refresh_token(self):
        url = os.path.join(self._get_endpoint('service.auth0.url'), 'oauth', 'token')
        data = {
            'audience': 'mycloud.com',
            'client_id': settings.WD_CLIENT_ID,
            'client_secret': settings.WD_CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': self.REFRESH_TOKEN
        }
        r = requests.post(url, data=data)
        self.ACCESS_TOKEN = r.json()['access_token']
        self.save()
        return r.json()

    def _check_access_token(self):
        if not self.ACCESS_TOKEN:
            return False
        url = os.path.join(self._get_endpoint('service.auth0.url'), 'userinfo')
        r = requests.get(url, headers=self._get_auth_headers(check=False))
        if r.text == 'Unauthorized':
            return False
        if r.json().get('error') == 'unauthorized':
            mail_admins('WD My Cloud Home is unauthorized', r.text)
            return False
        return True

    def _get_auth_headers(self, check=True):
        if check and not self._check_access_token():
            self._refresh_token()
        return {'Authorization': 'Bearer {}'.format(self.ACCESS_TOKEN)}

    def get_user_info(self):
        url = os.path.join(self._get_endpoint('service.auth0.url'), 'userinfo')
        r = requests.get(url, headers=self._get_auth_headers())
        self.USER_ID = r.json()['sub']
        self.save()
        return r.json()

    def get_user_devices(self):
        url = os.path.join(
            self._get_endpoint('service.device.url'), 'device', 'v1', 'user', self.USER_ID)
        r = requests.get(url, headers=self._get_auth_headers())
        data = r.json()['data'][0]
        self.DEVICE_ID = data['deviceId']
        self.DEVICE_NAME = data['name']
        self.DEVICE_INTERNAL_URL = data['network']['internalURL']
        self.DEVICE_EXTERNAL_URL = data['network']['externalURI']
        self.save()
        return r.json()

    def create_folder(self, name, directory='root'):
        url = os.path.join(self.DEVICE_INTERNAL_URL, 'sdk', 'v2', 'files')
        data = {
            'name': name,
            'mimeType': 'application/x.wd.dir',
            'parentID': directory
        }
        body, content_type = encode_media_related(data)
        headers = self._get_auth_headers()
        headers['Content-Type'] = content_type
        r = requests.post(url, data=body, headers=headers)
        return r

    def create_file(self, name, contents, directory='root'):
        url = os.path.join(self.DEVICE_INTERNAL_URL, 'sdk', 'v2', 'files')
        data = {
            'name': name,
            'parentID': directory
        }
        body, content_type = encode_media_related(data, contents)
        headers = self._get_auth_headers()
        headers['Content-Type'] = content_type
        r = requests.post(url, data=body, headers=headers)
        return r

    def get_files(self, directory='root'):
        url = os.path.join(self.DEVICE_INTERNAL_URL, 'sdk', 'v2', 'filesSearch', 'parents')
        params = {
            'ids': directory
        }
        r = requests.get(url, params=params, headers=self._get_auth_headers())
        return r.json()

    def delete_file(self, file_id):
        if file_id == self.APP_DIR_ID:
            return False
        url = os.path.join(self.DEVICE_INTERNAL_URL, 'sdk', 'v2', 'files', file_id)
        r = requests.delete(url, headers=self._get_auth_headers())
        return r

    def download_file(self, file_id):
        if file_id == self.APP_DIR_ID:
            return None
        url = os.path.join(self.DEVICE_INTERNAL_URL, 'sdk', 'v2', 'files', file_id, 'content')
        r = requests.get(url, headers=self._get_auth_headers())
        return r.content
