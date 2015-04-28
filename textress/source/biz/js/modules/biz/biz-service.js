define([
    './module'
], function(module) {
    'use strict';

    module.factory('Pricing', function($resource) {
        return $resource('/api/account/pricing/:id');
    });
});