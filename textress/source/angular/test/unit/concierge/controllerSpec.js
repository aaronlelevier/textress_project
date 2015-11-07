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

describe('GuestMessageCtrl', function() {
    var scope,
        ctrl,
        q,
        deferred,
        mockGuestUser,
        mockGuest,
        mockCurrentUser,
        mockCurrentUserResponse,
        mockGuestMessages;

    beforeEach(module('conciergeApp'));

    beforeEach(function() {

        mockGuest = {
            id: 1
        };
        module(function($provide) {
            $provide.value('GuestUser', mockGuest);
        });

        mockCurrentUser = {
            query: function() {
                deferred = q.defer();
                return {$promise: deferred.promise};
            }
        };
        
        spyOn(mockCurrentUser, 'query').andCallThrough();

        module(function($provide) {
            $provide.value('CurrentUser', mockCurrentUser);
        });

        mockGuestMessages = {
            get: function(id) {
                return {
                    'id': id
                };
            }
        };
        module(function($provide) {
            $provide.value('GuestMessages', mockGuestMessages);
        });

    });

    beforeEach(inject(function($rootScope, $controller, $q, GuestUser, CurrentUser, GuestMessages) {
        q = $q;
        scope = $rootScope.$new();
        ctrl = $controller('GuestMessageCtrl', {
            $scope: scope
        });
        mockGuestUser = GuestUser;
        mockCurrentUser = CurrentUser;
        mockGuestMessages = GuestMessages;
    }));

    it('init values', function() {
        expect(scope.messages).toEqual({});
        expect(scope.modal_msg).toEqual(0);
    });

    it('GuestUser.id', function() {
        expect(mockGuestUser.id).toEqual(1);
    });

    it('CurrentUser - API', inject(function($httpBackend) {
        // $httpBackend.expectGET("/api/current-user/");
        // $httpBackend.whenGET("/api/current-user/").respond({
        //     id: 2
        // });
        expect(mockCurrentUser.query).toHaveBeenCalled();

        // var user = mockCurrentUser.query();

        // deferred.resolve({id: 1});
        // scope.$apply();

        // console.log(user);
        // console.log(user.$promise);
        // // $httpBackend.flush();

        // scope.$apply();

        // expect(user.$promise.id).toEqual(2);
    }));

    it('$scope.user results', function() {
        mockCurrentUserResponse = {id: 1};
        deferred.resolve(mockCurrentUserResponse);
        scope.$apply();

        expect(scope.user.$promise.$$state.value.id).toEqual(mockCurrentUserResponse.id);
    });

    it('GuestMessages - API', inject(function($httpBackend) {
        // $httpBackend.expectGET("/api/current-user/");
        // $httpBackend.whenGET("/api/current-user/").respond(null);

        var guestMessages = mockGuestMessages.get(1);
        // $httpBackend.flush();

        expect(guestMessages.id).toEqual(1);
    }));

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

    // module(function($provide) {
    //     $provide.value('GuestUser', mockGuestUser);
    // });

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

    beforeEach(module('conciergeApp'));

    beforeEach(inject(function($rootScope, $controller) {
        scope = $rootScope.$new();
        ctrl = $controller('ReplyCtrl', {
            $scope: scope
        });
    }));

    it('init values', function() {
        expect(scope.reply).toEqual(null);
        expect(scope.letter).toEqual(null);
    })
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