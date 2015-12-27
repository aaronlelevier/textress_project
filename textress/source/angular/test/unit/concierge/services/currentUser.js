'use strict';

describe('Service: CurrentUser', function() {

  // load the service's module
  beforeEach(module('conciergeApp'));

  // instantiate service
  var CurrentUser;
  var $httpBackend;

  beforeEach(inject(function(_$httpBackend_, _CurrentUser_) {
    CurrentUser = _CurrentUser_;
    $httpBackend = _$httpBackend_;
  }));

  it('should do something', function() {
    expect(!!CurrentUser).toBe(true);
  });

  it('should query', function() {
    $httpBackend.expectGET('/api/current-user/').respond(200, {
      "id": 1,
      "hotel_id": 2
    });

    var data = CurrentUser.query();

    $httpBackend.flush();
    expect(data.id).toBe(1);
    expect(data.hotel_id).toBe(2);
  });

  afterEach(function() {
    $httpBackend.verifyNoOutstandingExpectation;
    $httpBackend.verifyNoOutstandingRequest;
  });
});