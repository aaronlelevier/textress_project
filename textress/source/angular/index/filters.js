angular.module('indexFilters', [])
    .filter('stripe_money', function() {
        return function(number) {
            return number / 100.0;
        };
    });