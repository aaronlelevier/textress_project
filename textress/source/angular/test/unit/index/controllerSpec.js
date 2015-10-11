/* jasmine specs for controllers go here */
describe('PricingCtrl', function() {

    beforeEach(module('indexApp'));
    beforeEach(inject(function($rootScope, $controller) {
        scope = $rootScope.$new();
        ctrl = $controller('PricingCtrl', {
            $scope: scope
        });
    }));

    it('init values', function() {
        expect(scope.volumes.length).toBe(4);
        expect(scope.volume).toBe("");
    });

});