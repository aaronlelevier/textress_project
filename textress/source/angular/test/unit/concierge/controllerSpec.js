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
   var mockUser = {
            id: 1,
            hotel_id: 1
        },
        mockGuest = {
            id: 1,
        },
        mockUserSvc, mockGuestSvc, scope, ctrl  ;

    beforeEach(module('conciergeApp', function($provide) {
        $provide.value('CurrentUser', mockUser);
    }));

    beforeEach(module('conciergeApp', function($provide) {
        $provide.value('GuestUser', mockGuest);
    }));

    beforeEach(inject(function(CurrentUser, GuestUser, $rootScope, $controller) {
        mockUserSvc = CurrentUser;
        mockGuestSvc = GuestUser;
        scope = $rootScope.$new();
        ctrl = $controller('GuestMessageCtrl', {
            $scope: scope
        });
    }));

    // CurrentUser Tests

    it('CurrentUser.id', function() {
        expect(mockUserSvc.id).toEqual(mockUser.id);
    });

    it('CurrentUser.hotel_id', function() {
        expect(mockUserSvc.hotel_id).toEqual(mockUser.hotel_id);
    });

    // GuestUser Tests

    it('GuestUser.id', function() {
        expect(mockGuestSvc.id).toEqual(mockGuest.id);
    })

    it('init values', function() {
        expect(scope.messages).toEqual({});
        expect(scope.modal_msg).toEqual(0);
        expect(scope.user_id).toEqual(1);
    })
});

describe('ReplyCtrl', function() {
   var mockData = {
            id: 1,
            hotel_id: 1
        }, mockUtilSvc, scope, ctrl  ;

    beforeEach(module('conciergeApp', function($provide) {
        $provide.value('CurrentUser', mockData);
    }));

    beforeEach(inject(function(CurrentUser, $rootScope, $controller) {
        mockUtilSvc = CurrentUser;
        scope = $rootScope.$new();
        ctrl = $controller('ReplyCtrl', {
            $scope: scope
        });
    }));

    it('init values', function() {
        expect(scope.hotel_id).toEqual(1);
        expect(scope.reply).toEqual(null);
        expect(scope.letter).toEqual(null);
    })
});

describe('TriggerCtrl', function() {
   var mockData = {
            id: 1,
            hotel_id: 1
        }, mockUtilSvc, scope, ctrl  ;

    beforeEach(module('conciergeApp', function($provide) {
        $provide.value('CurrentUser', mockData);
    }));

    beforeEach(inject(function(CurrentUser, $rootScope, $controller) {
        mockUtilSvc = CurrentUser;
        scope = $rootScope.$new();
        ctrl = $controller('TriggerCtrl', {
            $scope: scope
        });
    }));

    it('init values', function() {
        expect(scope.hotel_id).toEqual(1);
        expect(scope.reply).toEqual(null);
        expect(scope.trigger).toEqual(null);
        expect(scope.trigger_type).toEqual(null);
    })
});
