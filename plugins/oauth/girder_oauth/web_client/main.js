import { restRequest } from '@girder/core/rest';
import { splitRoute } from '@girder/core/misc';
import { fetchCurrentUser, setCurrentToken } from '@girder/core/auth';


import './routes';

// Extends and overrides API
import './views/LoginView';
import './views/RegisterView';
import './views/App';

// If the current URL contains a `girderToken` query parameter, set the current token to its value
const girderToken = new URLSearchParams(window.location.search).get('girderToken');

if (girderToken) {
    // This means we have been redirected from a successful OAuth login.
    // Save the token, and delete the query parameter from the URL.
    window.localStorage.setItem('girderToken', girderToken);
    setCurrentToken(girderToken);

    const queryParams = new URLSearchParams(window.location.search);
    queryParams.delete('girderToken');
    window.location.search = queryParams.toString();
}

/*

// login to keycloak if user not logged in
var afterFetch = (user) => {
    var redirect = splitRoute(window.location.href).base;
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
*/
