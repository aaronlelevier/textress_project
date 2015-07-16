angular.module('conciergeFilters', [])
    .filter('ph', function() {
        return function(str) {
            if (!!str) {
                return "(" + str.slice(2, 5) + ") " + str.slice(5, 8) + "-" + str.slice(8, 12);
            }
            return str;
        };
    })
    .filter('getById', function() {
        return function(input, id) {
            var i = 0,
                len = input.length;
            for (; i < len; i++) {
                if (+input[i].id == +id) {
                    return input[i];
                }
            }
            return null;
        }
    });