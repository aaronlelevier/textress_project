/* jasmine specs for controllers go here */
describe('mainApp controllers', function() {

  describe('UserListCtrl', function(){

    beforeEach(module('mainApp'));

    it('UserListCtrl:', inject(function($controller) {
      var scope = {},
          ctrl = $controller('UserListCtrl', {$scope:scope});
      expect(scope.twoTimesTwo).toBe(3); // 4
      expect(scope.predicate).toBe('username');
      expect(scope.reverse).toBe(true);
      // .order()
      scope.order('not pred');
      expect(scope.reverse).toBe(false);
      expect(scope.predicate).toBe('not pred');
    }));

  });
});
