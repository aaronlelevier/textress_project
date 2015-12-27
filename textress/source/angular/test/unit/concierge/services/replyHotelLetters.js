'use strict';

describe('Service: ReplyHotelLetters', function() {

  // load the service's module
  beforeEach(module('conciergeApp'));

  // instantiate service
  var ReplyHotelLetters;
  var $httpBackend;
  var replyLetters;

  replyLetters = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Z"
  ];

  beforeEach(inject(function(_$httpBackend_, _ReplyHotelLetters_) {
    ReplyHotelLetters = _ReplyHotelLetters_;
    $httpBackend = _$httpBackend_;
  }));

  it('should do something', function() {
    expect(!!ReplyHotelLetters).toBe(true);
  });

  it('should query', function() {
    $httpBackend.expectGET('/api/reply/hotel-letters/').respond(200, replyLetters);

    var data = ReplyHotelLetters.query();

    $httpBackend.flush();
    expect(data[0]).toBe("A");
    expect(data[1]).toBe("B");
  });

  afterEach(function() {
    $httpBackend.verifyNoOutstandingExpectation;
    $httpBackend.verifyNoOutstandingRequest;
  });
});