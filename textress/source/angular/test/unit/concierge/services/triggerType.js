'use strict';

describe('Service: TriggerType', function() {

  // load the service's module
  beforeEach(module('conciergeApp'));

  // instantiate service
  var TriggerType;
  var $httpBackend;
  var triggerTypeResponse;

  triggerTypeResponse = [{
    "id": 1,
    "name": "check_in",
    "human_name": "check in",
    "desc": "welcome message to send at check-in"
  }, {
    "id": 2,
    "name": "check_out",
    "human_name": "check out",
    "desc": "check-out thank you message"
  }];

  beforeEach(inject(function(_$httpBackend_, _TriggerType_) {
    TriggerType = _TriggerType_;
    $httpBackend = _$httpBackend_;
  }));

  it('should do something', function() {
    expect(!!TriggerType).toBe(true);
  });

  it('should query', function() {
    $httpBackend.expectGET('/api/trigger-type/').respond(200, triggerTypeResponse);

    var data = TriggerType.query();

    $httpBackend.flush();
    expect(data[0].id).toBe(1);
    expect(data[0].name).toBe("check_in");
    expect(data[0].human_name).toBe("check in");
    expect(data[0].desc).toBe("welcome message to send at check-in");
  });

  afterEach(function() {
    $httpBackend.verifyNoOutstandingExpectation;
    $httpBackend.verifyNoOutstandingRequest;
  });
});