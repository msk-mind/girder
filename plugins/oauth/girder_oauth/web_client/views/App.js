import App from '@girder/core/views/App'
import { restRequest } from '@girder/core/rest';
import { splitRoute } from '@girder/core/misc';
import { wrap } from '@girder/core/utilities/PluginUtils';
import { fetchCurrentUser } from '@girder/core/auth';

wrap(App, 'start', function (start) {
    // login to default OAuth2 provider
    var redirect = start.redirect || splitRoute(window.location.href).base;

    var afterFetch = (user) => {
        if (!user) {
            restRequest({
                url: 'oauth/provider',
                data: {
                    redirect: redirect
                } }).done((resp) => {
                if ('Keycloak' in resp) {
                    window.location = resp['Keycloak']
                }
            })
        }
    }

    fetchCurrentUser().done(afterFetch);

    start.call(this);

})
