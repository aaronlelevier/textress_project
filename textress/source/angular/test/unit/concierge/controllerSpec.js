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

    beforeEach(module('conciergeApp'));

    var scope,
        ctrl,
        q,
        deferred,
        mockGuestUser,
        mockGuest,
        mockCurrentUser,
        mockGuestMessages;

    beforeEach(function() {

        mockGuest = {
            id: 1
        };
        module(function($provide) {
            $provide.value('GuestUser', mockGuest);
        });

      mockGuestMessages = {
          get: function (id) {
              return {'id': id};
          }
      };

      module(function ($provide) {
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
        spyOn(mockGuestMessages, 'get').andCallThrough(1);

        // $httpBackend.expectGET("/api/guest-messages/1/");
        // $httpBackend.whenGET("/api/guest-messages/1/").respond({id: 1});

        $httpBackend.expectGET("/api/current-user/");
        $httpBackend.whenGET("/api/current-user/").respond({ id: 2});
        
        var user = mockCurrentUser.query();

        $httpBackend.flush();

        expect(user.id).toEqual(2);
    }));

    it('GuestMessages - API', inject(function($httpBackend) {
        $httpBackend.expectGET("/api/current-user/");
        $httpBackend.whenGET("/api/current-user/").respond({ id: 2});

        spyOn(mockCurrentUser, 'query').andCallThrough();

        var guestMessages = spyOn(mockGuestMessages, 'get').andCallThrough(1);
        
        var guestMessages = mockGuestMessages.get(1);

        $httpBackend.flush();

        expect(guestMessages.id).toEqual(1);
    }));

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