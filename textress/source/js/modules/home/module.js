define([
    'angular',
    'ui.router',
    '../../config'
], function(angular) {
    'use strict';

    return angular.module('app.home', [
        'app.constants',
        'ui.router'
    ]).config(function($stateProvider, $urlRouterProvider) {

        $urlRouterProvider.otherwise('/');

        $stateProvider
            .state('home', {
                url: '/',
                views: {
                    'css': {
                        templateUrl: '/source/templates/css.html'
                    },
                    'content@': {
                        templateUrl: '/source/js/modules/home/templates/home.html',
                        controller: 'IndexCtrl'
                    },
                    'page-css': {
                        templateUrl: '/source/js/modules/home/templates/home-css.html'
                    }
                }
            })
            .state('home.pricing', {
                url: '^/pricing',
                views: {
                    'content@': {
                        templateUrl: '/source/js/modules/home/templates/pricing.html',
                        controller: 'PricingCtrl'
                    }
                }
            })
            .state('home.features', {
                url: '^/features',
                views: {
                    'content@': {
                        templateUrl: '/source/js/modules/home/templates/features.html',
                        controller: 'FeaturesCtrl'
                    }
                }
            })
            .state('home.features.smsDemo', {
                url: '^/features/sms-demo',
                views: {
                    'content@': {
                        templateUrl: '/source/js/modules/home/templates/sms.html',
                        controller: 'SMSDemoCtrl'
                    },
                    'css@': {},
                    'page-css@': {}
                }
            })
            .state('home.contact', {
                url: '^/contact',
                views: {
                    'content@': {
                        templateUrl: '/source/js/modules/home/templates/contact.html',
                        controller: 'ContactCtrl'
                    }
                }
            });
    });
});