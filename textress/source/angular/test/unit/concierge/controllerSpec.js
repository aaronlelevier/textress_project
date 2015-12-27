describe('GuestListCtrl', function() {
  var $q,
    $rootScope,
    $scope,
    ctrl,
    mockGuest,
    mockGuestResponse = [{
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

  beforeEach(module('conciergeApp'));

  beforeEach(inject(function(_$q_, _$rootScope_) {
    $q = _$q_;
    $rootScope = _$rootScope_;
  }));

  beforeEach(inject(function($controller) {
    $scope = $rootScope.$new();

    mockGuest = {
      query: function() {
        guestDeferred = $q.defer();
        return {
          $promise: guestDeferred.promise
        };
      }
    }
    spyOn(mockGuest, 'query').andCallThrough();

    ctrl = $controller('GuestListCtrl', {
      '$scope': $scope,
      'Guest': mockGuest
    });
  }));

  describe('test initial static values', function() {
    it('init values', function() {
      expect($scope.predicate).toBe('messages[0].read');
      expect($scope.reverse).toBe(false);
    });

    it('$scope.order - same field', function() {
      var predicate = 'name';
      $scope.order(predicate);
      expect($scope.reverse).toBe(false);
      expect($scope.predicate).toBe(predicate);
    });

    it('$scope.order - different field', function() {
      var predicate = 'foo';
      $scope.order(predicate);
      expect($scope.reverse).toBe(false);
      expect($scope.predicate).toBe(predicate);
    });
  });

  describe('Guest', function() {
    beforeEach(function() {
      guestDeferred.resolve(mockGuestResponse)
      $rootScope.$apply();
    });

    it('query called', function() {
      expect(mockGuest.query).toHaveBeenCalled();
    });

    it('query - response', function() {
      expect($scope.guests).toEqual(mockGuestResponse);
    });
  });

});

describe('GuestMsgPreviewCtrl', function() {
  var $q,
    $rootScope,
    $scope,
    ctrl,
    mockGuestMessages,
    mockGuestMessagesResponse = {
      "id": 1,
      "name": "Scott",
      "room_number": "129",
      "phone_number": "+17023012823",
      "icon": {
        "name": "dog",
        "icon": "http://localhost:8000/media/icons/dog.gif"
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
        "sid": "SMbbf1853d9a0146ccb716a03a14af6b60",
        "received": true,
        "status": null,
        "to_ph": "+17023012823",
        "from_ph": "+17024302691",
        "body": "Thank you for staying.",
        "reason": null,
        "cost": null,
        "read": true,
        "created": "2015-10-26T13:35:39.848108Z",
        "modified": "2015-10-26T13:35:39.848133Z",
        "hidden": false
      }]
    };

  beforeEach(module('conciergeApp'));

  beforeEach(inject(function(_$q_, _$rootScope_) {
    $q = _$q_;
    $rootScope = _$rootScope_;
  }));

  beforeEach(inject(function($controller) {
    $scope = $rootScope.$new();

    mockGuestMessages = {
      query: function() {
        guestMessagesDeferred = $q.defer();
        return {
          $promise: guestMessagesDeferred.promise
        };
      }
    }
    spyOn(mockGuestMessages, 'query').andCallThrough();

    ctrl = $controller('GuestMsgPreviewCtrl', {
      '$scope': $scope,
      'GuestMessages': mockGuestMessages
    });
  }));

  describe('GuestMessages.get:', function() {
    beforeEach(function() {
      guestMessagesDeferred.resolve(mockGuestMessagesResponse);
      $rootScope.$apply();
    });

    it('query called', function() {
      expect(mockGuestMessages.query).toHaveBeenCalled();
    });

    it('query - response', function() {
      expect($scope.guests).toEqual(mockGuestMessagesResponse);
    });
  });

});

describe('GuestMessageCtrl:', function() {
  var $q,
    $rootScope,
    $scope,
    ctrl,
    mockCurrentUser,
    mockCurrentUserResponse = {
      'id': 1,
      'hotel': 1
    },
    mockGuestUser = {
      'id': 1
    },
    mockGuestMessages,
    mockGuestMessagesResponse = {
      "id": 1,
      "name": "Scott",
      "room_number": "129",
      "phone_number": "+17023012823",
      "icon": {
        "name": "dog",
        "icon": "http://localhost:8000/media/icons/dog.gif"
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
        "sid": "SMbbf1853d9a0146ccb716a03a14af6b60",
        "received": true,
        "status": null,
        "to_ph": "+17023012823",
        "from_ph": "+17024302691",
        "body": "Thank you for staying.",
        "reason": null,
        "cost": null,
        "read": true,
        "created": "2015-10-26T13:35:39.848108Z",
        "modified": "2015-10-26T13:35:39.848133Z",
        "hidden": false
      }]
    };

  beforeEach(module('conciergeApp'));

  beforeEach(inject(function(_$q_, _$rootScope_) {
    $q = _$q_;
    $rootScope = _$rootScope_;
  }));

  beforeEach(inject(function($controller) {
    $scope = $rootScope.$new();

    mockCurrentUser = {
      query: function() {
        currentUserDeferred = $q.defer();
        return {
          $promise: currentUserDeferred.promise
        };
      }
    }
    spyOn(mockCurrentUser, 'query').andCallThrough();

    mockGuestMessages = {
      get: function() {
        guestMessagesDeferred = $q.defer();
        return {
          $promise: guestMessagesDeferred.promise
        };
      }
    }
    spyOn(mockGuestMessages, 'get').andCallThrough();

    ctrl = $controller('GuestMessageCtrl', {
      '$scope': $scope,
      'CurrentUser': mockCurrentUser,
      'GuestUser': mockGuestUser,
      'GuestMessages': mockGuestMessages
    });
  }));

  describe('CurrentUser.query:', function() {
    beforeEach(function() {
      currentUserDeferred.resolve(mockCurrentUserResponse)
      guestMessagesDeferred.resolve(mockGuestMessagesResponse);
      $rootScope.$apply();
    });

    it('should query the CurrentUser', function() {
      expect(mockCurrentUser.query).toHaveBeenCalled();
    });

    it('set $scope.user_id based on CurrentUser.query', function() {
      expect($scope.user_id).toEqual(mockCurrentUserResponse.id);
    });
  });

  describe('GuestUser:', function() {
    it('id', function() {
      expect(mockGuestUser.id).toEqual(1);
    });
  });

  describe('GuestMessages.get:', function() {
    beforeEach(function() {
      guestMessagesDeferred.resolve(mockGuestMessagesResponse);
      $rootScope.$apply();
    });

    it('request called', function() {
      expect(mockGuestMessages.get).toHaveBeenCalled();
    });

    it('this.getGuest - is a function', function() {
      expect(ctrl['getGuest']).toBeDefined();
      expect(ctrl.getGuest instanceof Function).toBeTruthy();
    });

    // TODO: Can't get the scope to populate when calling this function
    // it('this.getGuest - call function', function() {
    //     ctrl.getGuest();
    //     console.log(mockGuestUser);
    //     console.log($scope.guest);
    //     console.log($scope.to);
    //     console.log($scope.messages);
    //     expect($scope.to).toEqual(mockGuestMessagesResponse.phone_number);
    // });
  });

  describe('init static values:', function() {
    it('all', function() {
      expect($scope.messages).toEqual({});
      expect($scope.modal_msg).toEqual(0);
    });
  });

});


describe('ReplyCtrl', function() {
  var $q,
    $rootScope,
    $scope,
    ctrl,
    mockCurrentUser,
    mockCurrentUserResponse = {
      'id': 1,
      'hotel': 1
    },
    mockReply,
    mockReplyResponse = [{
      "id": 2,
      "hotel": null,
      "letter": "Y",
      "desc": "Messaging Reactivated",
      "message": "None"
    }, {
      "id": 30,
      "hotel": 1,
      "letter": "T",
      "desc": "Thanks",
      "message": "Thank you for staying."
    }],
    mockReplyHotelLetters,
    mockReplyHotelLettersResponse = [
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

  beforeEach(module('conciergeApp'));

  beforeEach(inject(function(_$q_, _$rootScope_, _$httpBackend_) {
    $q = _$q_;
    $rootScope = _$rootScope_;
    $httpBackend = _$httpBackend_;
  }));

  beforeEach(inject(function($controller) {
    $scope = $rootScope.$new();

    mockCurrentUser = {
      query: function() {
        currentUserDeferred = $q.defer();
        return {
          $promise: currentUserDeferred.promise
        };
      }
    }
    spyOn(mockCurrentUser, 'query').andCallThrough();

    mockReply = {
      query: function() {
        replyDeferred = $q.defer();
        return {
          $promise: replyDeferred.promise
        };
      }
    }
    spyOn(mockReply, 'query').andCallThrough();

    mockReplyHotelLetters = {
      query: function() {
        replyHotelLettersDeferred = $q.defer();
        return {
          $promise: replyHotelLettersDeferred.promise
        };
      }
    }
    spyOn(mockReplyHotelLetters, 'query').andCallThrough();

    ctrl = $controller('ReplyCtrl', {
      '$scope': $scope,
      'CurrentUser': mockCurrentUser,
      'Reply': mockReply,
      'ReplyHotelLetters': mockReplyHotelLetters
    });

  }));

  it('init static values', function() {
    expect($scope.reply).toEqual(null);
    expect($scope.letter).toEqual(null);
  });

  describe('CurrentUser:', function() {
    beforeEach(function() {
      currentUserDeferred.resolve(mockCurrentUserResponse);
      $rootScope.$apply();
    });

    it('should query the CurrentUser', function() {
      expect(mockCurrentUser.query).toHaveBeenCalled();
    });

    it('set $scope.user_id based on CurrentUser.query', function() {
      expect($scope.hotel_id).toEqual(mockCurrentUserResponse.hotel_id);
    });
  });

  describe('HotelReplyLetters', function() {
    beforeEach(function() {
      replyHotelLettersDeferred.resolve(mockReplyHotelLettersResponse);
      $rootScope.$apply();
    });

    it('query should be called', function() {
      expect(mockReplyHotelLetters.query).toHaveBeenCalled();
    });

    it('system_replies', function() {
      expect($scope.hotel_letters).toEqual(mockReplyHotelLettersResponse);
    });
  });

  describe('query', function() {
    var Reply;
    var $httpBackend;
    // beforeEach(module('conciergeApp.services'));
    beforeEach(inject(function(_Reply_, _$httpBackend_) {
      Reply = _Reply_;
      $httpBackend = _$httpBackend_;
    }));

    afterEach(function() {
      $httpBackend.verifyNoOutstandingExpectation();
      $httpBackend.verifyNoOutstandingRequest();
    });

    it('should be a function', function() {
      expect(Reply.query).toBeDefined();
      expect(typeof Reply.query).toBe('function');
    });

    it('GET Hotel Replies: using hotel id', function() {
      var id = 1234;
      var mockResponse = [];
      $httpBackend.expect('GET', '/api/reply/?hotel=' + id).respond(mockResponse);

      Reply.query({
        hotel: id
      });
      $httpBackend.flush();
    });

    it('GET System Replies: where hotel id is NULL', function() {
      var mockResponse = [];
      $httpBackend.expect('GET', '/api/reply/?hotel__isnull=true').respond(mockResponse);

      Reply.query({
        hotel__isnull: true
      });
      $httpBackend.flush();
    });

  });
});


describe('TriggerCtrl', function() {
  var $q,
    $rootScope,
    $scope,
    ctrl,
    mockCurrentUser,
    mockCurrentUserResponse = {
      'id': 1,
      'hotel': 1
    },
    mockReply,
    mockReplyResponse = [{
      "id": 2,
      "hotel": null,
      "letter": "Y",
      "desc": "Messaging Reactivated",
      "message": "None"
    }, {
      "id": 30,
      "hotel": 1,
      "letter": "T",
      "desc": "Thanks",
      "message": "Thank you for staying."
    }],
    mockTrigger,
    mockTriggerResponse = [{
      "id": 6,
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
      },
      "hotel": 1
    }],
    mockTriggerType,
    mockTriggerTypeResponse = [{
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

  beforeEach(module('conciergeApp'));

  beforeEach(inject(function(_$q_, _$rootScope_) {
    $q = _$q_;
    $rootScope = _$rootScope_;
  }));

  beforeEach(inject(function($controller) {
    $scope = $rootScope.$new();

    mockCurrentUser = {
      query: function() {
        currentUserDeferred = $q.defer();
        return {
          $promise: currentUserDeferred.promise
        };
      }
    }
    spyOn(mockCurrentUser, 'query').andCallThrough();

    mockReply = {
      query: function() {
        replyDeferred = $q.defer();
        return {
          $promise: replyDeferred.promise
        };
      }
    }
    spyOn(mockReply, 'query').andCallThrough();

    mockTrigger = {
      query: function() {
        triggerDeferred = $q.defer();
        return {
          $promise: triggerDeferred.promise
        };
      }
    }
    spyOn(mockTrigger, 'query').andCallThrough();

    mockTriggerType = {
      query: function() {
        triggerTypeDeferred = $q.defer();
        return {
          $promise: triggerTypeDeferred.promise
        };
      }
    }
    spyOn(mockTriggerType, 'query').andCallThrough();

    ctrl = $controller('TriggerCtrl', {
      '$scope': $scope,
      'CurrentUser': mockCurrentUser,
      'Reply': mockReply,
      'Trigger': mockTrigger,
      'TriggerType': mockTriggerType
    });

  }));

  it('init values', function() {
    expect($scope.reply).toEqual(null);
    expect($scope.trigger).toEqual(null);
    expect($scope.trigger_type).toEqual(null);
  });

  describe('CurrentUser:', function() {
    beforeEach(function() {
      currentUserDeferred.resolve(mockCurrentUserResponse);
      $rootScope.$apply();
    });

    it('should query the CurrentUser', function() {
      expect(mockCurrentUser.query).toHaveBeenCalled();
    });

    it('set $scope.user_id based on CurrentUser.query', function() {
      expect($scope.hotel_id).toEqual(mockCurrentUserResponse.hotel_id);
    });
  });

  describe('Trigger', function() {
    beforeEach(function() {
      triggerDeferred.resolve(mockTriggerResponse);
      $rootScope.$apply();
    });

    it('query is called', function() {
      expect(mockTrigger.query).toHaveBeenCalled();
    });

    it('query - response', function() {
      expect($scope.triggers).toEqual(mockTriggerResponse);
    });
  });

  describe('TriggerType', function() {
    beforeEach(function() {
      triggerTypeDeferred.resolve(mockTriggerTypeResponse);
      $rootScope.$apply();
    });

    it('query is called', function() {
      expect(mockTriggerType.query).toHaveBeenCalled();
    });

    it('query - response', function() {
      expect($scope.trigger_type).toEqual(mockTriggerTypeResponse);
    });
  });

});