/**
 * Auth controller definition
 */
define([
    './module'
], function(module) {
    'use strict';

    module.controller('LoginCtrl', ['$scope', 'Auth', function($scope, Auth) {
        $scope.user = {};
        $scope.login = function(user) {
            Auth.login(user.username, user.password);
        }

    }]);

    module.controller('RegisterCtrl', ['$scope', 'Auth', function($scope, Auth) {
        $scope.user = {};

        $scope.register = function(user) {
            Auth.register(user.username, user.password, user.email);
        }
    }]);

});