define([
    'angular',
    'ui.router',
    '../../config'
], function(angular) {
    'use strict';

    return angular.module('app.auth', [
        'app.constants',
        'ui.router'
    ]).config(function($stateProvider, $urlRouterProvider) {

        $urlRouterProvider.otherwise('/');

        $stateProvider
            .state('auth', {
                url: '/',
                views: {
                    'css': {
                        templateUrl: '/source/templates/css.html'
                    },
                    'js': {
                        templateUrl: '/source/templates/js.html'
                    }
                }
            })
            .state('auth.login', {
                url: '^/login',
                views: {
                    'content@': {
                        templateUrl: '/source/js/modules/auth/templates/login.html',
                        controller: 'LoginCtrl'
                    }
                }
            })
            .state('auth.register', {
                url: '^/register',
                views: {
                    'content@': {
                        templateUrl: '/source/js/modules/auth/templates/register.html',
                        controller: 'RegisterCtrl'
                    }
                }
            })
    });

});