var conciergeControllers = angular.module('conciergeApp.controllers', ['conciergeApp.services']);

conciergeControllers.controller('GuestListCtrl', ['$scope', 'Guest', function($scope, Guest) {
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
        $scope.modal_msg = 0;
        $scope.user_id = CurrentUser.id;

        // Guest (single)
        $scope.getGuest = function(GuestMessages, $stateParams, $scope) {
            GuestMessages.get({
                id: GuestUser.id //$stateParams.guestId
            }, function(response) {
                $scope.guest = response;
                $scope.to = response.phone_number;
                $scope.messages = response.messages;
            });
        }
        
        // populate initial context without a delay
        $scope.getGuest(GuestMessages, $stateParams, $scope);

        $scope.submitMessage = function(body) {
            $scope.body = null;

            var message = new Message({
                to_ph: $scope.to,
                guest: $scope.guest.id,
                user: $scope.user_id,
                body: body
            });

            message.$save(function() {
                $scope.messages.unshift(message);
            });
        }

        // set flag to not call gm() on page load using $timeout. So the 
        // previous message isn't added to $scope.messages upon page load
        // ref: http://stackoverflow.com/questions/16947771/how-do-i-ignore-the-initial-load-when-watching-model-changes-in-angularjs
        var initializing = true;

        $scope.getMessage = function(message) {

            var gm = function(Message, $stateParams, $scope, message) {
                message = JSON.parse(message);

                Message.get({
                    id: message.id
                }, function(response) {
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