var indexControllers = angular.module('indexApp.controllers', []);

indexControllers.controller('PricingCtrl', ['$scope', 'Pricing',
    function($scope, Pricing) {
        //prices will be from a DRF REST endpoint, so when changed in the DB,
        //they are auto-reflected here
        Pricing.query({
            hotel__isnull: true
        }).$promise.then(function(response) {
            $scope.price = response[0].cost
        });

    }
]);