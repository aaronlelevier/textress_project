angular.module('mainApp.services', ['ngResource'])
    .factory('User', function($resource) {
        return $resource('/api/users/:id');
    });