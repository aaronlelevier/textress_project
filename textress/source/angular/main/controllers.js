var mainControllers = angular.module('mainApp.controllers', ['mainApp.services']);

mainControllers.controller('UserListCtrl', ['$scope', 'User', function($scope, User) {
    // test
    $scope.twoTimesTwo = 2 * 2;
    // live
    $scope.users = User.query();

    // Sorting for List
    $scope.predicate = 'username';
    $scope.reverse = true;
    $scope.order = function(predicate) {
        $scope.reverse = ($scope.predicate === predicate) ? !$scope.reverse : false;
        $scope.predicate = predicate;
    };
}]);