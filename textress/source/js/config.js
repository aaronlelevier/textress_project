/**
 * Defines constants for application
 */
define([
    'angular',
    'ngResource',
    'ui.bootstrap'
], function(angular) {
    'use strict';

    return angular.module('app.constants', [
            'ngResource',
            'ui.bootstrap'
        ])
        .config(function($interpolateProvider, $httpProvider, $resourceProvider, $locationProvider) {
            // dif brackets from django
            $interpolateProvider.startSymbol('[[').endSymbol(']]');

            // CSRF Support
            $httpProvider.defaults.xsrfCookieName = 'csrftoken';
            $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

            // This only works in angular 3!
            // It makes dealing with Django slashes at the end of everything easier.
            $resourceProvider.defaults.stripTrailingSlashes = false;

            //Http Intercpetor to check auth failures for xhr requests, auto-attaches `token`
            //for JWT Token Auth w/ DRF
            $httpProvider.interceptors.push('AuthInterceptor');

            //Removes /#/ URL element
            $locationProvider.html5Mode(true).hashPrefix('!');
        })
        .controller('DropdownCtrl', function($scope) {
            console.log('DropdownCtrl');

            $scope.hoveringOver = function(value) {
                $scope.overDropdown = true;
                console.log('hovering over');
            };
        })
        // must config as final ?
        .constant('CONFIG', {});
});