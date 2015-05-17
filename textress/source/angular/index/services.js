angular.module('indexApp.services', ['ngResource'])
    .factory('Pricing', function($resource) {
        return $resource('/api/account/pricing/:id');
    });