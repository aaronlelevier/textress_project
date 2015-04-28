define(['./module'], function(module) {
    'use strict';

    module.controller('ConciergeCtrl', ['$scope', function($scope) {
        $scope.twoTimesTwo = 2 * 2;
    }]);

    module.controller('StatsCtrl', ['$scope', 'Message', function($scope, Message) {
        $scope.messages = Message.query();
    }]);

    module.controller('MessageCtrl', ['$scope', '$stateParams', '$interval', 'Message', 'GuestMessages',
        function($scope, $stateParams, $interval, Message, GuestMessages) {
            $scope.messages = {};

            $scope.getGuest = function(GuestMessages, $stateParams, $scope) {
                    GuestMessages.get({
                        id: $stateParams.guestId
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

            $interval(function() {
                $scope.getGuest(GuestMessages, $stateParams, $scope);
            }, 10000);

            $scope.submitMessage = function(body) {
                console.log('Pre create - guest id:', $scope.guest.id);

                var message = new Message({
                    to_ph: $scope.to,
                    guest: $scope.guest.id,
                    body: body
                });

                // TODO: remove all console.log checkes b/4 Production
                console.log('guest id:', $scope.guest.id);

                message.$save(function() {
                    $scope.messages.unshift(message);
                    $scope.body = null;

                    // Guest submitted to save
                    console.log('Guest submitted ID:', $scope.guest)
                });
            }
        }
    ]);

});