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

describe('ReplyCtrl', function() {

    beforeEach(module('conciergeApp'));

    beforeEach(module(function($provide) {
        $provide.service('CurrentUser', function() {
            return 1;
        });
    }));

    //Getting reference of the mocked service
    var mockUtilSvc;

    inject(function(CurrentUser) {
        mockUtilSvc = CurrentUser;
    });

    beforeEach(inject(function($rootScope, $controller) {
        scope = $rootScope.$new();
        ctrl = $controller('ReplyCtrl', {
            $scope: scope
        });
    }));

    it('should return value from mock dependency', inject(function(mockUtilSvc) {
        expect(mockUtilSvc()).toEqual(1);
    }));

});
