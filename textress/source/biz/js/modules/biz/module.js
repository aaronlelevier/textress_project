define([
    'angular',
    'ui.router',
    'ng.django.forms',
    '../../config'
], function(angular) {
    'use strict';

    return angular.module('app.biz', [
        'app.constants',
        'ui.router',
        'ng.django.forms'
    ]).config(function($stateProvider, $urlRouterProvider) {

        $urlRouterProvider.otherwise('/');

        $stateProvider
            .state('pricing', {
                url: '/pricing/',
                views: {
                    'content@': {
                        templateUrl: '/source/biz/js/modules/biz/templates/pricing.html',
                        controller: 'PricingCtrl'
                    }
                }
            });
    });
});