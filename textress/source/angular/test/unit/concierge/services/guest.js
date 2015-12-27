'use strict';

describe('Service: Guest', function() {

  // load the service's module
  beforeEach(module('conciergeApp'));

  // instantiate service
  var Guest;
  var $httpBackend;
  var guestResponse;

  guestResponse = [{
    "id": 2,
    "name": "Scott",
    "room_number": "129",
    "phone_number": "+17023012823",
    "icon": {
      "name": "dog",
      "icon": "/media/icons/dog.gif"
    },
    "check_in": "2015-10-09",
    "check_out": "2015-10-10",
    "created": "2015-10-09T02:44:43.060582Z",
    "modified": "2015-11-01T22:28:08.729131Z",
    "hidden": false,
    "messages": [{
      "id": 144,
      "guest": 2,
      "user": 1,
      "read": true
    }, {
      "id": 141,
      "guest": 2,
      "user": 1,
      "read": true
    }]
  }];

  beforeEach(inject(function(_$httpBackend_, _Guest_) {
    Guest = _Guest_;
    $httpBackend = _$httpBackend_;
  }));

  it('should do something', function() {
    expect(!!Guest).toBe(true);
  });

  it('should query', function() {
    $httpBackend.expectGET('/api/guests/').respond(200, guestResponse);

    var data = Guest.query();

    $httpBackend.flush();

    expect(data[0].id).toBe(2);
    expect(data[0].name).toBe("Scott");
  });

  afterEach(function() {
    $httpBackend.verifyNoOutstandingExpectation;
    $httpBackend.verifyNoOutstandingRequest;
  });
});