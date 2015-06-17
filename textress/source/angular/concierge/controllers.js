var conciergeControllers = angular.module('conciergeApp.controllers', ['conciergeApp.services']);

conciergeControllers.controller('ConciergeCtrl', ['$scope', function($scope) {
    $scope.twoTimesTwo = 2 * 2;
}]);

conciergeControllers.controller('StatsCtrl', ['$scope', 'Message', function($scope, Message) {
    $scope.messages = Message.query();
}]);

conciergeControllers.controller('GuestListCtrl', ['$scope', 'Guest', function($scope, Guest) {
    // test
    $scope.twoTimesTwo = 2 * 2;
    // live
    $scope.guests = Guest.query();

    // Sorting for List
    $scope.predicate = 'name';
    $scope.reverse = true;
    $scope.order = function(predicate) {
        $scope.reverse = ($scope.predicate === predicate) ? !$scope.reverse : false;
        $scope.predicate = predicate;
    };
}]);

conciergeControllers.controller('GuestMessageCtrl',
    ['$scope', '$stateParams', '$timeout', 'Message', 'GuestMessages', 'GuestUser', 'CurrentUser',
    function($scope, $stateParams, $timeout, Message, GuestMessages, GuestUser, CurrentUser) {
        $scope.messages = {};

        $scope.user_id = CurrentUser.id;
        console.log('User ID:', CurrentUser.id);

        // Guest (single)
        $scope.getGuest = function(GuestMessages, $stateParams, $scope) {
            GuestMessages.get({
                id: GuestUser.id //$stateParams.guestId
            }, function(response) {
                $scope.guest = response;
                $scope.to = response.phone_number;
                $scope.messages = response.messages;

                // test
                console.log('Guest:', $scope.guest);
            });
        }
        
        // populate initial context without a delay
        $scope.getGuest(GuestMessages, $stateParams, $scope);

        $scope.submitMessage = function(body) {
            console.log('Pre create - guest id:', $scope.guest.id);
            $scope.body = null;

            var message = new Message({
                to_ph: $scope.to,
                guest: $scope.guest.id,
                user: $scope.user_id,
                body: body
            });

            message.$save(function() {
                console.log('$save unshift:', message)
                $scope.messages.unshift(message);
                // moved to top to clear faster, so User isn't waiting
                // $scope.body = null; 

                // Guest submitted to save
                console.log('Post create - guest:', $scope.guest)
            });
        }

        // set flag to not call getMsg() on page load using $timeout.
        // ref: http://stackoverflow.com/questions/16947771/how-do-i-ignore-the-initial-load-when-watching-model-changes-in-angularjs
        var initializing = true;

        $scope.getMessage = function(message) {

            var gm = function(Message, $stateParams, $scope, message) {
                console.log(message);
                message = JSON.parse(message);
                console.log(typeof(message));
                var a = message;
                console.log(a.sid);

                Message.get({
                    id: message.id //$stateParams.guestId
                }, function(response) {
                    // test
                    console.log('getMessage:', response);
                    $scope.messages.unshift(response);
                });
            }
            if (initializing) {
                $timeout(function() { initializing = false; });
            } else {
                gm(Message, $stateParams, $scope, message);
            }
        }
    }
]);