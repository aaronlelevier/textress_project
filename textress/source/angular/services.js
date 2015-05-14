angular.module('homeApp.services', ['ngResource'])
    .factory('Pricing', function($resource) {
        return $resource('/api/account/pricing/:id');
    });