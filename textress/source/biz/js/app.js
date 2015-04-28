/**
 * loads sub modules and wraps them up into the main module.
 * This should be used for top-level module definitions only.
 */
define([
    'angular',
    'ngResource',
    'ui.router',
    'ng.django.forms',
    './config',
    './modules/biz/index'
], function(angular) {
    'use strict';

    return angular.module('app', [
        'app.constants',
        'app.biz',
        'ngResource',
        'ui.router',
        'ng.django.forms'
    ]);
});