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

        $scope.getMessage = function(message) {

            // get the # of Guests
            var i = 0;
            var obj = $scope.guests;
            var arr = Object.keys(obj).map(function(key) {
                return obj[key]
            });
            var len = arr.length;
            console.log('messages len:', len);

            Message.get({
                id: message.id
            }, function(response) {
                // append response (msg) to the guest
                console.log('response:',response);
                var i = 0,
                    len = $scope.guests.length;
                for (; i < len; i++) {
                    if (+$scope.guests[i].id == +response.guest.id) {
                        $scope.guests[i].messages.unshift(message);
                        console.log('if triggered:', $scope.guests[i]);
                    }
                }
            });

            // for (; i < len; i++) {
            //     if (+$scope.guests[i].id == +message.guest.id) {
            //         $scope.guests[i].messages.unshift(message);
            //         console.log('if triggered:', $scope.guests[i]);
            //     }
            // }

            // var gm = function(Message, $stateParams, $scope, message) {
            //     message = JSON.parse(message);
            //     console.log('getMessage():', message);

            //     Message.get({
            //         id: message.id
            //     }, function(response) {
            //         // append response (msg) to the guest
            //         var i = 0,
            //             len = $scope.guests.length;
            //         for (; i < len; i++) {
            //             if (+$scope.guests[i].id == +response.guest.id) {
            //                 $scope.guests[i].messages.unshift(response);
            //             }
            //         }
            //     });

            // if (initializing) {
            //     $timeout(function() {
            //         initializing = false;
            //     });
            // } else {
            // gm(Message, $stateParams, $scope, message);
            // }
            // }

        }
    }
    // TODO: figure out how to add Msg Counts to the template
]);

// Use for single GuestDetail page w/ SMS messages. Send/Receive SMS
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
                $timeout(function() {
                    initializing = false;
                });
            } else {
                gm(Message, $stateParams, $scope, message);
            }
        }
    }
]);