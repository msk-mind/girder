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
        return
        f"http://{settings.get(PluginSettings.KEYCLOAK_HOSTNAME)}:{settings.get(PluginSettings.KEYCLOAK_PORT)}/realms/{settings.get(PluginSettings.KEYCLOAK_REALM)}/protocol/openid-connect"

    @staticmethod
    def getAuthUrl():
        return Keycloak.getOidcUrl() + "/auth"

    @staticmethod
    def getTokenUrl(self):
        return Keycloak.getOidcUrl() + "/token"

    @staticmethod
    def getUserinfoUrl(self):
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

        # Because the token came directly from Keycloak API, we don't need to verify it
        payload = jwt.decode(idToken, verify=False)

        oauthId = payload['sub']

        email = payload.get('email')
        if not email:
            raise RestException('This Keycloak user has no available email address.', code=502)

        # The user's full name is in the payload, but is not split into first and last names

        discovery = self._getJson(method='GET', url=self._DISCOVERY_URL)
        userinfoUrl = Keycloak.getUserinfoUrl()

        userinfo = self._getJson(method='GET', url=userinfoUrl, headers={
            'Authorization': '%s %s' % (token['token_type'], token['access_token'])
        })
        firstName = userinfo.get('given_name', '')
        lastName = userinfo.get('family_name', '')

        user = self._createOrReuseUser(oauthId, email, firstName, lastName)
        return user
