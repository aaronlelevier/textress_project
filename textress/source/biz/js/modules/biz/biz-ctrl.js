define([
    './module'
], function(module) {
    'use strict';

    module.controller('PricingCtrl', ['$scope', 'Pricing', function($scope, Pricing) {
        //prices will be from a DRF REST endpoint, so when changed in the DB,
        //they are auto-reflected here
        $scope.prices = Pricing.query();

        $scope.volumes = [500, 2500, 5000, 7500];

        $scope.volume = "";
        $scope.submit_volume = function(volume) {
            $scope.volume = volume;
        }

        // calculate SMS cost
        $scope.calc_cost = function() {
            $scope.cost = 0;
            angular.forEach($scope.prices, function(p) {
                if ($scope.volume >= p.end) {
                    $scope.cost += p.price * (p.end - p.start + 1);
                } else if ($scope.volume >= p.start && $scope.volume < p.end) {
                    $scope.cost += p.price * ($scope.volume - p.start + 1);
                }
            });
            return $scope.cost;
        }

        $scope.$watch(
            'volume',
            function(newValue) {
                return newValue;
            });
    }]);
});