'use strict';

describe('Service: MessageSendWelcome', function() {

  // load the service's module
  beforeEach(module('conciergeApp'));

  // instantiate service
  var MessageSendWelcome;
  var $httpBackend;
  var phNums;

  phNums = {
    "0": "+17754194000",
    "1": "+17023012823"
  };

  beforeEach(inject(function(_$httpBackend_, _MessageSendWelcome_) {
    MessageSendWelcome = _MessageSendWelcome_;
    $httpBackend = _$httpBackend_;
  }));

  it('should do something', function() {
    expect(!!MessageSendWelcome).toBe(true);
  });

  it('post dict of phNums', function() {
    var response = phNums;
    $httpBackend.whenPOST('/api/messages/send-welcome/', phNums).respond(response);

    var data = new MessageSendWelcome(phNums);
    data.$save();

    expect(data['0']).toBe(phNums['0']);
    expect(data['1']).toBe(phNums['1']);
  });

  // TODO: need to bring in controller w/ `send` method
  // it('use $scope.input in send() to send phNums', function() {
  //   var response = phNums;
  //   $httpBackend.whenPOST('/api/messages/send-welcome/', phNums).respond(response);
  // });

  afterEach(function() {
    $httpBackend.verifyNoOutstandingExpectation;
    $httpBackend.verifyNoOutstandingRequest;
  });
});