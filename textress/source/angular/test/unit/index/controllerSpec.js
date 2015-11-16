// describe('Concierge App', function () {
//     describe('PricingCtrl Controller', function () {
//         var Pricing;
//         var PricingCtrl;
//         var $scope;
//         var PricingQueryMock;
//         var HOTEL_ID = 1234;
//         beforeEach(module('indexApp'));
//         beforeEach(inject(function (_Pricing_, $controller, $rootScope) {
//             // This object can be used throughout your controller unit test for the
//             // response of calling the Pricing.query method
//             PricingQueryMock = {};
//             Pricing = _Pricing_;
//             spyOn(Pricing, 'query').andReturn(PricingQueryMock);
//             $scope = $rootScope.$new();
//             $scope.hotel_id = HOTEL_ID;
//             PricingCtrl = $controller('PricingCtrl', {$scope: $scope});
//         }));

//         it('should populate hotel_replies', function () {
//             expect(Pricing.query).toHaveBeenCalledWith({
//                 hotel: HOTEL_ID
//             });
//             expect($scope.hotel_replies).toBe(PricingQueryMock);
//         });
//     });
    
//     // don't necessarily need to test $resource internals
//     describe('Pricing Resource', function () {
//         var Pricing;
//         var $resource;
//         var PricingResourceMock;
//         beforeEach(module('conciergeApp.services', function ($provide) {
//             // Mock out $resource here
//             $provide.factory('$resource', function () {
//                 PricingResourceMock = {};
//                 var $resource = jasmine.createSpy('$resource');
//                 $resource.and.returnValue(PricingResourceMock);
//                 return $resource;
//             });
//         }));
//         beforeEach(inject(function (_Pricing_, _$resource_) {
//             Pricing = _Pricing_;
//             $resource = _$resource_;
//         }));

//         it('should initialize resource', function () {
//             expect($resource).toHaveBeenCalledWith('/api/reply/:id/');
//             expect(Pricing).toBe(PricingResourceMock);
//         });
//     });
    
//     // Example of testing the internals of $resource
//     describe('Pricing Backend', function () {
//         var Pricing;
//         var $httpBackend;
//         beforeEach(module('conciergeApp.services'));
//         beforeEach(inject(function (_Pricing_, _$httpBackend_) {
//             Pricing = _Pricing_;
//             $httpBackend = _$httpBackend_;
//         }));

//         afterEach(function () {
//             $httpBackend.verifyNoOutstandingExpectation();
//             $httpBackend.verifyNoOutstandingRequest();
//         });

//         describe('query', function () {
//             it('should be a function', function () {
//                 expect(Pricing.query).toBeDefined();
//                 expect(typeof Pricing.query).toBe('function');
//             });

//             it('should delegate to correct url using hotel id', function () {
//                 var id = 1234;
//                 var mockResponse = [];
//                 $httpBackend.expect('GET', '/api/reply?hotel=' + id).respond(mockResponse);

//                 Pricing.query({
//                     hotel: id
//                 });
//                 $httpBackend.flush();
//             });
//         });
//     });
    
// });
