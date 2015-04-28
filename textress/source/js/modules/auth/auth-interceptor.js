define(['./module'], function(module) {
    'use strict';

    module.service('AuthInterceptor', function($injector, $location, $q) {
        var AuthInterceptor = {
            request: function(config) {
                var Auth = $injector.get('Auth');
                var token = Auth.getToken();

                if (token) {
                    config.headers['Authorization'] = 'JWT ' + token;
                }
                return config;
            },

            responseError: function(response) {
                if (response.status === 403) {
                    if (response.data.detial === 'Signature has expired.') {
                        $location.path('/login');
                    }
                }
                return $q.reject(response);
            }
        };

        return AuthInterceptor;
    });
});