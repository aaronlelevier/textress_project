'use strict';

describe('Service: Trigger', function() {

  // load the service's module
  beforeEach(module('conciergeApp'));

  // instantiate service
  var Trigger;
  var $httpBackend;
  var triggerResponse;

  triggerResponse = [{
    "id": 6,
    "hotel": 1,
    "type": {
      "id": 2,
      "name": "check_out",
      "human_name": "check out",
      "desc": "check-out thank you message"
    },
    "reply": {
      "id": 30,
      "hotel": 1,
      "letter": "T",
      "desc": "Thanks",
      "message": "Thank you for staying."
    }
  }];

  beforeEach(inject(function(_$httpBackend_, _Trigger_) {
    Trigger = _Trigger_;
    $httpBackend = _$httpBackend_;
  }));

  it('should do something', function() {
    expect(!!Trigger).toBe(true);
  });

  it('should query', function() {
    $httpBackend.expectGET('/api/trigger/').respond(200, triggerResponse);

    var data = Trigger.query();

    $httpBackend.flush();
    expect(data[0].id).toBe(6);
    expect(data[0].hotel).toBe(1);
    expect(data[0].type.id).toBe(2);
    expect(data[0].type.name).toBe("check_out");
    expect(data[0].reply.id).toBe(30);
    expect(data[0].reply.hotel).toBe(1);
    expect(data[0].reply.letter).toBe("T");
  });

  it('should update - update the Reply associated w/ the Trigger', function() {
    var trigger = triggerResponse[0];
    var newReply = {
      "id": 3,
      "hotel": 1,
      "letter": "T",
      "desc": "Thanks",
      "message": "My new Thank you y'all"
    };
    trigger.reply = newReply;
    $httpBackend.whenPATCH('/api/trigger/6/', trigger).respond(200, trigger);

    var data = Trigger.update({
      id: 6
    }, trigger);

    $httpBackend.flush();
    expect(data.id).toBe(6);
    expect(data.reply.id).toBe(newReply.id);
    expect(data.reply.message).toBe(newReply.message);
  });

  it('should delete', function() {
    $httpBackend.whenDELETE('/api/trigger/1/').respond();

    var trigger = new Trigger(triggerResponse[0]);
    trigger.$remove({
      id: triggerResponse[0].id
    });
  });

  afterEach(function() {
    $httpBackend.verifyNoOutstandingExpectation;
    $httpBackend.verifyNoOutstandingRequest;
  });
});