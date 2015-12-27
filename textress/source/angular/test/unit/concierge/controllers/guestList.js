describe('Controller: GuestListCtrl', function() {

  beforeEach(module('conciergeApp'));

  var GuestListCtrl;
  var scope;
  var q;
  var deferred;
  var guests;
  var mockGuest;

  beforeEach(function() {
    guests = [{
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
    }],
    mockGuest = {
      query: function() {
        deferred = q.defer();
        return {
          $promise: deferred.promise
        };
      }
    },
    mockMessage = {
      get: function(message) {
        deferred = q.defer();
        return {
          $promise: deferred.promise
        };
      }
    }
  });

  // Initialize the controller and a mock scope
  beforeEach(inject(function($rootScope, $q, _$controller_) {
    q = $q;
    scope = $rootScope.$new();
    $controller = _$controller_;

    GuestListCtrl = $controller('GuestListCtrl', {
      $scope: scope,
      Guest: mockGuest,
      Message: mockMessage
    });
  }));

  it('should have static init values', function() {
    expect(scope.predicate).toBe('messages[0].read');
    expect(scope.reverse).toBe(false);
    expect(scope.initializing).toBe(true);
  });

  it('should populate scope.guests', function() {
    spyOn(mockGuest, 'query').andCallThrough();

    deferred.resolve(guests);
    scope.$root.$digest();

    expect(scope.guests).toEqual(guests);
  });

  it('scope.order - same field', function() {
    var predicate = 'name';

    scope.order(predicate);

    expect(scope.reverse).toBe(false);
    expect(scope.predicate).toBe(predicate);

    // call a 2nd time
    scope.order(predicate);
    expect(scope.reverse).toBe(true);
  });

  it('scope.getMessage - matches - so gets pushed onto their message list', function() {
    spyOn(mockGuest, 'query').andCallThrough();
    deferred.resolve(guests);
    scope.$root.$digest();
    expect(scope.guests[0].messages.length).toEqual(2);
    var message = {
      "id": 10,
      "guest": 2,
      "user": 1,
      "read": false
    };

    spyOn(mockMessage, 'get').andCallThrough();
    deferred.resolve(message);
    scope.$root.$digest();
    scope.getMessage(message);

    // work on getting to pass
    // expect(mockMessage.get).toHaveBeenCalled();
    // expect(scope.guest, scope.guests[0]);
    // expect(scope.guests[0].messages.length).toEqual(3);
  });
});