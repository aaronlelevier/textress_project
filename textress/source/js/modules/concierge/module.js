define([
    'angular',
    'ngResource',
    'ui.router',
    'angular.filter',
    '../../config'
], function(angular) {
    'use strict';

    return angular.module('app.concierge', [
        'app.constants',
        'ngResource',
        'ui.router',
        'angular.filter'
    ]).config(function($stateProvider, $urlRouterProvider) {

        $urlRouterProvider.otherwise('/');

        $stateProvider
            .state('concierge', {
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
            .state('concierge.concierge', {
                url: '^/concierge',
                views: {
                    'content@': {
                        templateUrl: '/source/js/modules/concierge/templates/concierge.html',
                        controller: 'ConciergeCtrl'
                    }
                }
            })
            .state('concierge.stats', {
                url: '^/stats',
                views: {
                    'content@': {
                        templateUrl: '/source/js/modules/concierge/templates/stats.html',
                        controller: 'StatsCtrl'
                    }
                }
            })
            .state('concierge.messages', {
                url: '^/messages/:guestId',
                views: {
                    'content@': {
                        templateUrl: '/source/js/modules/concierge/templates/messages.html',
                        controller: 'MessageCtrl'
                    }
                }
            })
    });

});