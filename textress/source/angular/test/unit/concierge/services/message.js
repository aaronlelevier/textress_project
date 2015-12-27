'use strict';

describe('Service: Message', function() {

  // load the service's module
  beforeEach(module('conciergeApp'));

  // instantiate service
  var Message;
  var $httpBackend;
  var messageResponse;

  messageResponse = [{
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
    "read": false,
    "created": "2015-12-13T15:32:41.967039Z",
    "modified": "2015-12-13T15:32:41.967072Z",
    "hidden": false,
    "insert_date": "2015-12-13"
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
    "hidden": false,
    "insert_date": "2015-12-26"
  }];

  beforeEach(inject(function(_$httpBackend_, _Message_) {
    Message = _Message_;
    $httpBackend = _$httpBackend_;
  }));

  it('should do something', function() {
    expect(!!Message).toBe(true);
  });

  it('should query', function() {
    $httpBackend.expectGET('/api/messages/').respond(200, messageResponse);

    var data = Message.query();

    $httpBackend.flush();
    expect(data[0].id).toBe(1);
    expect(data[0].guest).toBe(1);
    expect(data[0].user).toBe(2);
  });

  it('should get', function() {
    $httpBackend.expectGET('/api/messages/1/').respond(200, messageResponse[0]);

    var data = Message.get({
      id: 1
    });

    $httpBackend.flush();
    expect(data.id).toBe(1);
    expect(data.guest).toBe(1);
    expect(data.user).toBe(2);
  });

  it('should get', function() {
    var msg = messageResponse[0];
    expect(msg.read).toBe(false);

    msg.read = true;
    $httpBackend.whenPATCH('/api/messages/1/', msg).respond(200, msg);

    var data = Message.update({
      id: 1
    }, msg);

    $httpBackend.flush();
    expect(data.id).toBe(1);
    expect(data.read).toBe(true);
  });

  afterEach(function() {
    $httpBackend.verifyNoOutstandingExpectation;
    $httpBackend.verifyNoOutstandingRequest;
  });
});