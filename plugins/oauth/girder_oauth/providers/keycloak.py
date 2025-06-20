# -*- coding: utf-8 -*-
import urllib.parse

import jwt

from girder.api.rest import getApiUrl
from girder.exceptions import RestException
from girder.models.setting import Setting

from .base import ProviderBase
from ..settings import PluginSettings


class Keycloak(ProviderBase):
    # https://developers.google.com/identity/protocols/OpenIDConnect
    #
    _AUTH_SCOPES = ['profile', 'email']

    @staticmethod
    def getOidcUrl():
        settings = Setting()
        return f"{settings.get(PluginSettings.KEYCLOAK_URL)}/realms/{settings.get(PluginSettings.KEYCLOAK_REALM)}/protocol/openid-connect"

    @staticmethod
    def getAuthUrl():
        return Keycloak.getOidcUrl() + "/auth"

    @staticmethod
    def getTokenUrl():
        return Keycloak.getOidcUrl() + "/token"

    @staticmethod
    def getUserinfoUrl():
        return Keycloak.getOidcUrl() + "/userinfo"


    def getClientIdSetting(self):
        return Setting().get(PluginSettings.KEYCLOAK_CLIENT_ID)

    def getClientSecretSetting(self):
        return Setting().get(PluginSettings.KEYCLOAK_CLIENT_SECRET)

    @classmethod
    def getUrl(cls, state):
        clientId = Setting().get(PluginSettings.KEYCLOAK_CLIENT_ID)
        if not clientId:
            raise Exception('No Keycloak client ID setting is present.')

        callbackUrl = '/'.join((getApiUrl(), 'oauth', 'keycloak', 'callback'))

        query = urllib.parse.urlencode({
            'response_type': 'code',
            'access_type': 'online',
            'client_id': clientId,
            'redirect_uri': callbackUrl,
            'state': state,
            'scope': 'openid %s' % ' '.join(cls._AUTH_SCOPES)
        })
        return '%s?%s' % (Keycloak.getAuthUrl(), query)

    def getToken(self, code):
        params = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.clientId,
            'client_secret': self.clientSecret,
            'redirect_uri': self.redirectUri
        }
        resp = self._getJson(method='POST', url=Keycloak.getTokenUrl(), data=params)
        return resp

    def getUser(self, token):
        idToken = token['id_token']

        payload = jwt.decode(idToken, algorithms=['HS256'], options={'verify_signature': False})

        oauthId = payload['sub']

        email = payload.get('email')
        if not email:
            raise RestException('This Keycloak user has no available email address.', code=502)

        # The user's full name is in the payload, but is not split into first and last names

        userinfoUrl = Keycloak.getUserinfoUrl()

        userinfo = self._getJson(method='GET', url=userinfoUrl, headers={
            'Authorization': '%s %s' % (token['token_type'], token['access_token'])
        })
        firstName = userinfo.get('given_name', '')
        lastName = userinfo.get('family_name', '')

        user = self._createOrReuseUser(oauthId, email, firstName, lastName)
        return user
