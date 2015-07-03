angular.module('conciergeApp.services', ['ngResource'])
    .factory('Guest', function($resource) {
        return $resource('/api/guests/:id');
    })
    .factory('Message', function($resource) {
        return $resource('/api/messages/:id');
    })
    .factory('GuestMessages', function($resource) {
        return $resource('/api/guest-messages/:id');
    });