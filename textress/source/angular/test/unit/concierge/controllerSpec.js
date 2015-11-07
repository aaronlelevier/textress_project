/* jasmine specs for controllers go here */
describe('GuestListCtrl', function() {

    beforeEach(module('conciergeApp'));

    beforeEach(inject(function($rootScope, $controller) {
        scope = $rootScope.$new();
        ctrl = $controller('GuestListCtrl', {
            $scope: scope
        });
    }));

    it('init values', function() {
        expect(scope.predicate).toBe('name');
        expect(scope.reverse).toBe(true);
    });

    it('$scope.order - same field', function() {
        var predicate = 'name';
        scope.order(predicate);
        expect(scope.reverse).toBe(false);
        expect(scope.predicate).toBe(predicate);
    });

    it('$scope.order - different field', function() {
        var predicate = 'foo';
        scope.order(predicate);
        expect(scope.reverse).toBe(false);
        expect(scope.predicate).toBe(predicate);
    });

});

describe('GuestMessageCtrl:', function() {
    var $q,
        $rootScope,
        $scope,
        ctrl,
        mockCurrentUser,
        mockCurrentUserResponse = {'id': 1, 'hotel': 1},
        mockGuestUser = {'id': 1},
        mockGuestMessages,
        mockGuestMessagesResponse = {
            "id": 1,
            "name": "Scott",
            "room_number": "129",
            "phone_number": "+17023012823",
            "icon": {
                "name": "dog",
                "icon": "http://localhost:8000/media/icons/dog.gif"
            },
            "check_in": "2015-10-09",
            "check_out": "2015-10-10",
            "created": "2015-10-09T02:44:43.060582Z",
            "modified": "2015-11-01T22:28:08.729131Z",
            "hidden": false,
            "messages": [
                {
                    "id": 144,
                    "guest": 2,
                    "user": 1,
                    "sid": "SMbbf1853d9a0146ccb716a03a14af6b60",
                    "received": true,
                    "status": null,
                    "to_ph": "+17023012823",
                    "from_ph": "+17024302691",
                    "body": "Thank you for staying.",
                    "reason": null,
                    "cost": null,
                    "read": true,
                    "created": "2015-10-26T13:35:39.848108Z",
                    "modified": "2015-10-26T13:35:39.848133Z",
                    "hidden": false
                }
            ]
        };

    beforeEach(module('conciergeApp'));

    beforeEach(inject(function(_$q_, _$rootScope_) {
        $q = _$q_;
        $rootScope = _$rootScope_;
    }));

    beforeEach(inject(function($controller) {
        $scope = $rootScope.$new();

        mockCurrentUser = {
            query: function() {
                currentUserDeferred = $q.defer();
                return {
                    $promise: currentUserDeferred.promise
                };
            }
        }
        spyOn(mockCurrentUser, 'query').andCallThrough();

        mockGuestMessages = {
            get: function() {
                guestMessagesDeferred = $q.defer();
                return {
                    $promise: guestMessagesDeferred.promise
                };
            }
        }
        spyOn(mockGuestMessages, 'get').andCallThrough();

        ctrl = $controller('GuestMessageCtrl', {
            '$scope': $scope,
            'CurrentUser': mockCurrentUser,
            'GuestUser': mockGuestUser,
            'GuestMessages': mockGuestMessages
        });
    }));

    describe('CurrentUser.query:', function() {

        beforeEach(function() {
            currentUserDeferred.resolve(mockCurrentUserResponse)
            guestMessagesDeferred.resolve(mockGuestMessagesResponse);
            $rootScope.$apply();
        });

        it('should query the CurrentUser', function() {
            expect(mockCurrentUser.query).toHaveBeenCalled();
        });

        it('set $scope.user_id based on CurrentUser.query', function() {
            expect($scope.user_id).toEqual(mockCurrentUserResponse.id);
        });

    });

    describe('GuestUser:', function() {
        it('id', function() {
            expect(mockGuestUser.id).toEqual(1);
        });
    });

    describe('GuestMessages.get:', function() {

        beforeEach(function() {
            currentUserDeferred.resolve(mockCurrentUserResponse)
            guestMessagesDeferred.resolve(mockGuestMessagesResponse);
            $rootScope.$apply();
        });

        it('request called', function() {
            expect(mockGuestMessages.get).toHaveBeenCalled();
        });

        it('this.getGuest - is a function', function() {
            expect(ctrl['getGuest']).toBeDefined();
            expect(ctrl.getGuest instanceof Function).toBeTruthy();
        });

        // TODO: Can't get the scope to populate when calling this function
        // it('this.getGuest - call function', function() {
        //     ctrl.getGuest();
        //     console.log(mockGuestUser);
        //     console.log($scope.guest);
        //     console.log($scope.to);
        //     console.log($scope.messages);
        //     expect($scope.to).toEqual(mockGuestMessagesResponse.phone_number);
        // });

    });

    describe('init static values:', function() {

        it('all', function() {
            expect($scope.messages).toEqual({});
            expect($scope.modal_msg).toEqual(0);
        });

    });

});


describe('ReplyCtrl', function() {
    var $q,
        $rootScope,
        $scope,
        ctrl,
        mockCurrentUser,
        mockCurrentUserResponse = {'id': 1, 'hotel': 1},
        mockReply,
        mockReplyResponse = [{
            "id": 2,
            "hotel": null,
            "letter": "Y",
            "desc": "Messaging Reactivated",
            "message": "None"
        }, {
            "id": 30,
            "hotel": 1,
            "letter": "T",
            "desc": "Thanks",
            "message": "Thank you for staying."
        }],
        mockReplyHotelLetters,
        mockReplyHotelLettersResponse = [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "L",
            "M",
            "N",
            "O",
            "P",
            "Q",
            "R",
            "T",
            "U",
            "V",
            "W",
            "X",
            "Z"
        ];

    beforeEach(module('conciergeApp'));

    beforeEach(inject(function(_$q_, _$rootScope_) {
        $q = _$q_;
        $rootScope = _$rootScope_;
    }));

    beforeEach(inject(function($controller) {
        $scope = $rootScope.$new();

        mockCurrentUser = {
            query: function() {
                currentUserDeferred = $q.defer();
                return {
                    $promise: currentUserDeferred.promise
                };
            }
        }
        spyOn(mockCurrentUser, 'query').andCallThrough();

        mockReply = {
            query: function() {
                replyDeferred = $q.defer();
                return {
                    $promise: replyDeferred.promise
                };
            }
        }
        spyOn(mockReply, 'query').andCallThrough();

        mockReplyHotelLetters = {
            query: function() {
                replyHotelLettersDeferred = $q.defer();
                return {
                    $promise: replyHotelLettersDeferred.promise
                };
            }
        }
        spyOn(mockReplyHotelLetters, 'query').andCallThrough();

        ctrl = $controller('ReplyCtrl', {
            '$scope': $scope,
            'CurrentUser': mockCurrentUser,
            'Reply': mockReply,
            'ReplyHotelLetters': mockReplyHotelLetters
        });

    }));

    it('init static values', function() {
        expect(scope.reply).toEqual(null);
        expect(scope.letter).toEqual(null);
    });

    describe('CurrentUser:', function() {

        beforeEach(function() {
            currentUserDeferred.resolve(mockCurrentUserResponse);
            $rootScope.$apply();
        });

        it('should query the CurrentUser', function() {
            expect(mockCurrentUser.query).toHaveBeenCalled();
        });

        it('set $scope.user_id based on CurrentUser.query', function() {
            expect($scope.hotel_id).toEqual(mockCurrentUserResponse.hotel_id);
        });
    });

    describe('HotelReplyLetters', function() {

        beforeEach(function() {
            replyHotelLettersDeferred.resolve(mockReplyHotelLettersResponse);
            $rootScope.$apply();
        });

        it('query should be called', function() {
            expect(mockReplyHotelLetters.query).toHaveBeenCalled();
        });

        it('system_replies', function() {
            expect($scope.hotel_letters).toEqual(mockReplyHotelLettersResponse);
        });

    });

});

describe('TriggerCtrl', function() {

    beforeEach(module('conciergeApp'));

    beforeEach(inject(function($rootScope, $controller) {
        scope = $rootScope.$new();
        ctrl = $controller('TriggerCtrl', {
            $scope: scope
        });
    }));

    it('init values', function() {
        expect(scope.reply).toEqual(null);
        expect(scope.trigger).toEqual(null);
        expect(scope.trigger_type).toEqual(null);
    })
});