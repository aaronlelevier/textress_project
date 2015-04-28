define(['./module'], function (module) {
    'use strict';

    module
        .factory('Guest', function($resource) {
            return $resource('/api/guests/:id');
        })
        .factory('Message', function($resource) {
            return $resource('/api/messages/:id');
        })
        .factory('GuestMessages', function($resource) {
            return $resource('/api/guest-messages/:id');
        })
        .factory('User', function($resource) {
            return $resource('/api/users/:id');
        });
});