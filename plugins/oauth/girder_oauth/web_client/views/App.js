import App from '@girder/core/views/App'
import { restRequest } from '@girder/core/rest';
import { splitRoute } from '@girder/core/misc';
import { wrap } from '@girder/core/utilities/PluginUtils';
import { fetchCurrentUser } from '@girder/core/auth';

wrap(App, 'initialize', function (initialize) {
    // login to default OAuth2 provider
    //
    var afterFetch = (user) => {
        if (!user) {
            restRequest({
                url: 'oauth/autologin_provider',
                data: {
                    redirect: window.location.href
                } }).done(
                    (resp) => {
                        if (resp)
                            window.location = resp['url']
                    }
                )
        }
    }

    fetchCurrentUser().done(afterFetch);


    initialize.call(this);
})
