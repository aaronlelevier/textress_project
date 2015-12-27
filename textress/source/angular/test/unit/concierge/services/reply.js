'use strict';

describe('Service: Reply', function() {

  // load the service's module
  beforeEach(module('conciergeApp'));

  // instantiate service
  var Reply;
  var $httpBackend;
  var hotelReplies;
  var systemReplies;

  hotelReplies = [{
    "id": 1,
    "hotel": 1,
    "letter": "T",
    "desc": "Thanks",
    "message": "Thank you for staying."
  }];

  systemReplies = [{
    "id": 2,
    "hotel": null,
    "letter": "Y",
    "desc": "Messaging Reactivated",
    "message": "None"
  }];

  beforeEach(inject(function(_$httpBackend_, _Reply_) {
    Reply = _Reply_;
    $httpBackend = _$httpBackend_;
  }));

  it('should do something', function() {
    expect(!!Reply).toBe(true);
  });

  it('should query using the hotel id', function() {
    $httpBackend.expectGET('/api/reply/?hotel=1').respond(200, hotelReplies);

    var data = Reply.query({
      hotel: 1
    });

    $httpBackend.flush();
    expect(data[0].id).toBe(1);
    expect(data[0].hotel).toBe(1);
    expect(data[0].letter).toBe("T");
  });

  it('should query where hotel id is null', function() {
    $httpBackend.expectGET('/api/reply/?hotel__isnull=true').respond(200, systemReplies);

    var data = Reply.query({
      hotel__isnull: true
    });

    $httpBackend.flush();
    expect(data[0].id).toBe(2);
    expect(data[0].hotel).toBeNull();
    expect(data[0].letter).toBe("Y");
  });

  it('should update', function() {
    var reply = hotelReplies[0];
    var newMessage = "My newMessage y'all";
    reply.message = newMessage;
    $httpBackend.whenPATCH('/api/reply/1/', reply).respond(200, reply);

    var data = Reply.update({
      id: 1
    }, reply);

    $httpBackend.flush();
    expect(data.id).toBe(1);
    expect(data.message).toBe(newMessage);
  });

  it('should create', function() {
    var reply = {
      "hotel": 1,
      "letter": "Z",
      "desc": "zoo",
      "message": "zoo message"
    };
    var response = reply;
    response.id = 3;
    $httpBackend.whenPOST('/api/reply/', reply).respond(response);

    var data = new Reply(reply);
    data.$save();

    expect(data.id).toBe(3);
    expect(data.hotel).toBe(1);
    expect(data.letter).toBe("Z");
    expect(data.desc).toBe("zoo");
    expect(data.message).toBe("zoo message");
  });

  it('should delete', function() {
    $httpBackend.whenDELETE('/api/reply/1/').respond();

    var reply = new Reply(hotelReplies[0]);
    reply.$remove({
      id: hotelReplies[0].id
    });
  });

  afterEach(function() {
    $httpBackend.verifyNoOutstandingExpectation;
    $httpBackend.verifyNoOutstandingRequest;
  });
});