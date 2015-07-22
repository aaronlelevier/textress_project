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

// Dashboard page, where new messages should pop via a websocke to dispay to the User
conciergeControllers.controller('GuestMsgPreviewCtrl', ['$scope', '$filter', '$stateParams', '$timeout', 'Message', 'GuestMessages',
    function($scope, $filter, $stateParams, $timeout, Message, GuestMessages) {

        $scope.guests = GuestMessages.query();

        // works. converts obj to array.
        var obj = $scope.guests;
        var arr = Object.keys(obj).map(function(key) {
            return obj[key]
        });

        var initializing = true;

        $scope.getMessage = function(message) {

            var gm = function(Message, $stateParams, $scope, message) {

                // get the # of Guests
                var i = 0;
                var obj = $scope.guests;
                var arr = Object.keys(obj).map(function(key) {
                    return obj[key]
                });
                console.log('message pre-JSON:', message);
                var len = arr.length;
                message = JSON.parse(message);
                console.log('message post-JSON:', message);
                // from the Message Obj, append it to the correct Guest's Messages
                Message.get({
                    id: message.id
                }, function(response) {
                    console.log('response:', response);
                    var i = 0,
                        len = $scope.guests.length;
                    for (; i < len; i++) {
                        if (+$scope.guests[i].id == +response.guest.id) {
                            $scope.guests[i].messages.unshift(message);
                            console.log('if triggered:', $scope.guests[i]);
                        }
                    }
                });

            }
            if (initializing) {
                $timeout(function() {
                    initializing = false;
                });
            } else {
                gm(Message, $stateParams, $scope, message);

            }
        }
    }
]);

// Use for single GuestDetail page w/ SMS messages. Send/Receive SMS
// GuestUser = Guest
conciergeControllers.controller('GuestMessageCtrl', ['$scope', '$stateParams', '$timeout', 'Message', 'GuestMessages', 'GuestUser', 'CurrentUser',
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

        $scope.submitMessage = function(ws4redis, body) {
            $scope.body = null;

            var message = new Message({
                to_ph: $scope.to,
                guest: $scope.guest.id,
                user: $scope.user_id,
                body: body
            });

            // `response` needed to get full object:
            // http://stackoverflow.com/questions/17131643/promise-on-angularjs-resource-save-action
            message.$save(function() {
                    $scope.messages.unshift(message);
                })
                .then(function(response) {
                    console.log('typeof:', typeof(response), 'id:', response.id, 'response:', response);
                    console.log('Acutual msg being sent:', JSON.stringify(response));
                    ws4redis.send_message(JSON.stringify(response));
                });
        }

        // set flag to not call gm() on page load using $timeout. So the 
        // previous message isn't added to $scope.messages upon page load
        // ref: http://stackoverflow.com/questions/16947771/how-do-i-ignore-the-initial-load-when-watching-model-changes-in-angularjs
        var initializing = true;

        $scope.getMessage = function(message) {

            var gm = function(message) {
                // `message` is an array when sent from the User/Guest's View.
                // when sitting on another view, and receiving from Redis, it is an object.
                // goal: convert to JSON in order to handle
                console.log('typeof:', typeof(message));
                console.log('message pre-JSON:', message);
                if (typeof(message) !== "object") {
                    message = JSON.parse(message);
                }
                // else {
                //     message = JSON.parse(message);                    
                // }
                console.log('message post-JSON:', message);
                console.log('typeof:', typeof(message));

                if (message.guest == GuestUser.id) {
                    Message.get({
                        id: message.id
                    }, function(response) {
                        // only append the Message if it belongs to the Guest
                        $scope.messages.unshift(response);
                    });
                }
            }

            if (initializing) {
                $timeout(function() {
                    initializing = false;
                });
            } else {
                gm(message);
            }
        }
    }
]);