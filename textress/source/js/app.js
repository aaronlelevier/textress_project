/**
 * loads sub modules and wraps them up into the main module.
 * This should be used for top-level module definitions only.
 */
define([
    'angular',
    'ngResource',
    'ngAnimate',
    'ui.router',
    'ui.bootstrap',
    'angular.filter',
    './config',
    './modules/docs/index',
    './modules/home/index',
    './modules/ui/index',
    './modules/concierge/index',
    './modules/auth/index'
], function(angular) {
    'use strict';

    return angular.module('app', [
        'app.constants',
        'app.docs',
        'app.home',
        'app.ui',
        'app.concierge',
        'app.auth',
        'ngResource',
        'ngAnimate',
        'ui.router',
        'ui.bootstrap',
        'angular.filter'
    ]);
});