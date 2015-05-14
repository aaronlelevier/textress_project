angular.module('homeApp', [
        'ui.router',
        'ngResource',
        'homeApp.services',
        'homeApp.controllers'
    ])
    .config(function($interpolateProvider, $httpProvider, $resourceProvider, $locationProvider) {
        // dif brackets from django
        $interpolateProvider.startSymbol('[[').endSymbol(']]');

        // Allow AJAX Post
        $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

        // CSRF Support
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';

        // This only works in angular 3!
        // It makes dealing with Django slashes at the end of everything easier.
        $resourceProvider.defaults.stripTrailingSlashes = false;

        //Removes /#/ URL element
        $locationProvider.html5Mode(true).hashPrefix('!');
    });