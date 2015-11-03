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
   var mockGuest = {
            id: 1,
        },
        mockGuestSvc, scope, ctrl  ;

    beforeEach(module('conciergeApp', function($provide) {
        $provide.value('GuestUser', mockGuest);
    }));

    beforeEach(inject(function(GuestUser, $rootScope, $controller) {
        mockGuestSvc = GuestUser;
        scope = $rootScope.$new();
        ctrl = $controller('GuestMessageCtrl', {
            $scope: scope
        });
    }));

    // GuestUser Tests

    it('GuestUser.id', function() {
        expect(mockGuestSvc.id).toEqual(mockGuest.id);
    })

    it('init values', function() {
        expect(scope.messages).toEqual({});
        expect(scope.modal_msg).toEqual(0);
    })
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
