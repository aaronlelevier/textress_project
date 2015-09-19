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
    })
    .filter('unreadMessages', function() {
        return function(items) {
            items.sort(function(a, b) {
                if (a.messages[0].read === false)
                    return 1;
                if (a.messages[0].read === true)
                    return -1;
                return 0;
            })
        }
    })
    .filter('numRead', function() {
        return function(guestArr) {
            return guestArr.filter(function(guest) {
                return guest.read === false;
            }).length
        }
    })
    .filter('lastMsg', function() {
        return function(guestArr, field) {
            return guestArr[0][field]
        };
    });


