'use strict';

describe('Service: GuestMessages', function() {

  // load the service's module
  beforeEach(module('conciergeApp'));

  // instantiate service
  var GuestMessages;
  var $httpBackend;
  var response;

  response = [{
    "id": 1,
    "name": "Dave Tanner",
    "room_number": "115",
    "phone_number": "+17754194000",
    "icon": {
      "name": "dog",
      "icon": "/media/icons/dog.gif"
    },
    "check_in": "2015-12-13",
    "check_out": "2015-12-14",
    "created": "2015-12-13T15:32:04.958616Z",
    "modified": "2015-12-26T14:36:04.565485Z",
    "hidden": false,
    "messages": [{
      "id": 3,
      "guest": 1,
      "user": 2,
      "sid": null,
      "received": false,
      "status": null,
      "to_ph": "+17754194000",
      "from_ph": "+17024302691",
      "body": "Welcome",
      "reason": "A 'From' phone number is required.",
      "cost": null,
      "read": true,
      "created": "2015-12-26T14:35:22.411067Z",
      "modified": "2015-12-26T14:35:22.411102Z",
      "hidden": false
    }, {
      "id": 2,
      "guest": 1,
      "user": 2,
      "sid": null,
      "received": false,
      "status": null,
      "to_ph": "+17754194000",
      "from_ph": "+17024302691",
      "body": "Yo",
      "reason": "A 'From' phone number is required.",
      "cost": null,
      "read": true,
      "created": "2015-12-26T14:34:31.147042Z",
      "modified": "2015-12-26T14:34:31.147071Z",
      "hidden": false
    }, {
      "id": 1,
      "guest": 1,
      "user": 2,
      "sid": null,
      "received": false,
      "status": null,
      "to_ph": "+17754194000",
      "from_ph": "+17024302691",
      "body": "Hi",
      "reason": "A 'From' phone number is required.",
      "cost": null,
      "read": true,
      "created": "2015-12-13T15:32:41.967039Z",
      "modified": "2015-12-13T15:32:41.967072Z",
      "hidden": false
    }]
  }];

  beforeEach(inject(function(_$httpBackend_, _GuestMessages_) {
    GuestMessages = _GuestMessages_;
    $httpBackend = _$httpBackend_;
  }));

  it('should do something', function() {
    expect(!!GuestMessages).toBe(true);
  });

  it('should query', function() {
    $httpBackend.expectGET('/api/guest-messages/').respond(200, response);

    var data = GuestMessages.query();

    $httpBackend.flush();
    expect(data[0].id).toBe(1);
    expect(data[0].name).toBe("Dave Tanner");
    expect(data[0].phone_number).toBe("+17754194000");
  });

  it('should get', function() {
    $httpBackend.expectGET('/api/guest-messages/1/').respond(200, response[0]);

    var data = GuestMessages.get({
      id: 1
    });

    $httpBackend.flush();
    expect(data.id).toBe(1);
    expect(data.name).toBe("Dave Tanner");
    expect(data.phone_number).toBe("+17754194000");
  });

  afterEach(function() {
    $httpBackend.verifyNoOutstandingExpectation;
    $httpBackend.verifyNoOutstandingRequest;
  });
});