var conciergeControllers = angular.module('conciergeApp.controllers', ['conciergeApp.services']);

conciergeControllers.controller('SendWelcomeCtrl', ['$scope', 'MessageSendWelcome',
  function($scope, MessageSendWelcome) {
    $scope.phNums = [null, null, null, null, null, null, null, null, null, null];
    $scope.errors = {};

    $scope.send = function(){
      for(var ph in $scope.phNums){
        if(!$scope.phNums[ph]){
          $scope.phNums[ph] = undefined;
        }
      }
      var messages = new MessageSendWelcome($scope.phNums);

      messages.$save(function() {
      }).then(function(response) {
        $scope.clear();
      }, function(error) {
        // handle error here by updating errors on page
        // should return a dict of ph:error msg
        $scope.errors = error;
      });
    }

    $scope.clear = function() {
      $scope.phNums = [null, null, null, null, null, null, null, null, null, null];
      $scope.errors = {};
    }
  }
]);

conciergeControllers.controller('GuestListCtrl', ['$scope', '$timeout', 'Guest', 'Message',
  function($scope, $timeout, Guest, Message) {

    // Sorting for List
    $scope.predicate = 'messages[0].read';
    $scope.reverse = false;

    Guest.query().$promise.then(function(response) {
      $scope.guests = response;
    });

    $scope.order = function(predicate) {
      $scope.reverse = ($scope.predicate === predicate) ? !$scope.reverse : false;
      $scope.predicate = predicate;
    };

    // GuestListView: Push incoming messsage onto Guest Messages array for all Guests
    $scope.initializing = true;

    $scope.getMessage = function(message) {

      var gm = function(message) {
        // goal: convert to JSON in order to handle
        if (typeof(message) !== "object") {
          message = JSON.parse(message);
        }

        for (i = 0; i < $scope.guests.length; i++) {
          if (message.guest == $scope.guests[i].id) {
            $scope.guest = $scope.guests[i]; // set as local $scope to the Ctrl otherwise
            // can't access it w/i `Message.get()` below
            Message.get({
              id: message.id
            }, function(response) {
              // Only append the Message if it belongs to the Guest
              // $scope.guests[i].messages.unshift(response);
              $scope.guest.messages.push(response);
            });
          }
        }
      }

      if ($scope.initializing) {
        $timeout(function() {
          $scope.initializing = false;
        });
      } else {
        gm(message);
      }
    }
  }
]);

// ``Dashboard page``: where new messages should pop via a websocket to dispay to the User
conciergeControllers.controller('GuestMsgPreviewCtrl', ['$scope', '$filter', '$stateParams', '$timeout', 'Message', 'GuestMessages',
  function($scope, $filter, $stateParams, $timeout, Message, GuestMessages) {

    // $scope.guests = GuestMessages.query();
    GuestMessages.query().$promise.then(function(response) {
      $scope.guests = response;
    });

    // Append Last Message object to each Guest in Array
    // LastMsg has: text, time, read/unread status

    // GuestListView: Push incoming messsage onto Guest Messages array for all Guests
    initializing = true;

    $scope.getMessage = function(message) {

      var gm = function(message) {
        // goal: convert to JSON in order to handle
        if (typeof(message) !== "object") {
          message = JSON.parse(message);
        }

        for (i = 0; i < $scope.guests.length; i++) {
          if (message.guest == $scope.guests[i].id) {
            $scope.guest = $scope.guests[i]; // set as local $scope to the Ctrl otherwise
            // can't access it w/i `Message.get()` below
            Message.get({
              id: message.id
            }, function(response) {
              // Only append the Message if it belongs to the Guest
              // $scope.guests[i].messages.unshift(response);
              $scope.guest.messages.push(response);
            });
          }
        }
      }

      if (initializing) {
        $timeout(function() {
          initializing = false;
        });
      } else {
        gm(message);
      }
    }
  }
]);

// Use for single GuestDetail page w/ SMS messages. Send/Receive SMS
// GuestUser = Guest
conciergeControllers.controller('GuestMessageCtrl', ['$scope', '$stateParams', '$timeout', 'Message', 'GuestMessages', 'GuestUser', 'CurrentUser',
  function($scope, $stateParams, $timeout, Message, GuestMessages, GuestUser, CurrentUser) {

    $scope.user = CurrentUser.query();
    $scope.user.$promise.then(function(result) {
      $scope.user_id = result.id;
    });

    $scope.messages = {};
    $scope.modal_msg = 0;

    // Guest (single)
    this.getGuest = function() {
      GuestMessages.get({
        id: GuestUser.id
      }, function(response) {
        $scope.guest = response;
        $scope.to = response.phone_number;
        $scope.messages = response.messages;
      });
    }

    // populate initial context without a delay
    this.getGuest();

    $scope.submitMessage = function(ws4redis, body) {
      $scope.body = null;

      var message = new Message({
        to_ph: $scope.to,
        guest: $scope.guest.id,
        user: $scope.user_id,
        body: body
      });

      // `response` needed to get full object:
      // http://stackoverflow.com/questions/17131643/promise-on-angularjs-resource-save-action
      message.$save(function() {
        $scope.messages.unshift(message);
      }).then(function(response) {
        // Comment out: only needed for debugging
        // console.log('typeof:', typeof(response), 'id:', response.id, 'response:', response);
        // console.log('Acutual msg being sent:', JSON.stringify(response));
        ws4redis.send_message(JSON.stringify(response));
      });
    }

    // set flag to not call gm() on page load using $timeout. So the 
    // previous message isn't added to $scope.messages upon page load
    // ref: http://stackoverflow.com/questions/16947771/how-do-i-ignore-the-initial-load-when-watching-model-changes-in-angularjs
    var initializing = true;

    $scope.getMessage = function(message) {

      var gm = function(message) {
        // `message` is an array when sent from the User/Guest's View.
        // when sitting on another view, and receiving from Redis, it is an object.
        // goal: convert to JSON in order to handle

        // Comment out: only needed for debugging
        // console.log('typeof:', typeof(message));
        // console.log('message pre-JSON:', message);
        if (typeof(message) !== "object") {
          message = JSON.parse(message);
        }
        // Comment out: only needed for debugging
        // console.log('message post-JSON:', message);
        // console.log('typeof:', typeof(message));

        if (message.guest == GuestUser.id) {
          Message.get({
            id: message.id
          }, function(response) {
            // Message should be marked as 'read=true' at this point because 
            //  is being rendered in the GuestDetailView to the User
            response.read = true;
            response.user = response.user || null;
            Message.update({
              id: response.id
            }, response);
            // Only append the Message if it belongs to the Guest
            $scope.messages.unshift(response);
          });
        }
      }

      if (initializing) {
        $timeout(function() {
          initializing = false;
        });
      } else {
        gm(message);
      }
    }
  }
]);


conciergeControllers.controller('ReplyTriggerCtrl',
  ['$scope', 'Reply', 'ReplyHotelLetters', 'Trigger', 'TriggerType', 'CurrentUser',
  function($scope, Reply, ReplyHotelLetters, Trigger, TriggerType, CurrentUser) {

    $scope.trigger_type = $scope.trigger = $scope.reply = $scope.letter = null;

    CurrentUser.query().$promise.then(function(result) {
      $scope.hotel_id = result.hotel_id;

      // do inside the `promise` so `hotel_id` is resolved 1st
      Reply.query({
        hotel: $scope.hotel_id
      }).$promise.then(function(response) {
        $scope.hotel_replies = response;
      })
    });

    Reply.query({
      hotel__isnull: true
    }).$promise.then(function(response) {
      $scope.system_replies = response;
    });

    ReplyHotelLetters.query().$promise.then(function(response) {
      $scope.hotel_letters = response;
    });

    $scope.$watch(function() {
        return $scope.letter;
      },
      function(newValue) {
        return newValue;
      });

    $scope.letterPicked = function(letter) {
      Reply.query({
        hotel: $scope.hotel_id,
        letter: letter
      }, function(response) {
        if (response[0]) {
          $scope.reply = response[0];
        } else {
          $scope.reply.desc = $scope.reply.message = "";
        }
      });
    }

    $scope.saveReply = function(reply) {
      if (reply.id) {
        Reply.update({
          id: reply.id
        }, reply);
        angular.forEach($scope.hotel_replies, function(u, i) {
          if (u.id === reply.id) {
            $scope.hotel_replies.splice(i, 1, reply);
          }
        })
      } else {
        var reply = new Reply({
          hotel: $scope.hotel_id,
          letter: reply.letter,
          desc: reply.desc || "",
          message: reply.message
        });
        reply.$save(function(response) {
            // Comment out: only needed for debugging
            // console.log(response);
          },
          function(err) {
            // Comment out: only needed for debugging
            // console.log(err);
          }).then(function(response) {
          $scope.hotel_replies.push(response);
        });;
      }
      $scope.reply = null;
      $scope.$digest;
    }

    $scope.deleteReply = function(reply) {

      angular.forEach($scope.hotel_replies, function(u, i) {
        if (u.id === reply.id) {
          $scope.hotel_replies.splice(i, 1);
        }
      })

      reply.$remove({
        id: reply.id
      });

      angular.forEach($scope.triggers, function(key, value) {
        if (reply.id === key.reply.id) {
          $scope.triggers.splice(value, 1);
        }
      })
    }

    $scope.trigger_types = TriggerType.query();
    $scope.triggers = Trigger.query();

    $scope.$watch(function() {
        return $scope.trigger;
      },
      function(newValue) {
        return newValue;
      }, true);

    $scope.$watch(function() {
        return $scope.reply;
      },
      function(newValue) {
        return newValue;
      });

    $scope.triggerTypePicked = function(trigger_type) {
      if (trigger_type) {
        var trigger_type = JSON.parse(trigger_type); // cuz sent from view.html as a string

        Trigger.query({
          type__id: trigger_type.id
        }).$promise.then(function(response) {
          if (response[0]) {
            $scope.trigger = response[0];
            $scope.reply_trigger = $scope.trigger.reply;
          } else {
            $scope.trigger = $scope.reply = null;
          }
        });
      } else {
        $scope.trigger = null;
      }
    }

    $scope.saveTrigger = function(trigger_type, reply) {

      // trigger, trigger_type, and reply -> are all local VARs that are objects
      var trigger = $scope.trigger;
      var trigger_type = JSON.parse(trigger_type);

      if (trigger) {

        Trigger.update({
          id: trigger.id
        }, {
          type: trigger_type.id,
          reply: reply.id
        });

        trigger.reply = reply;
        trigger.type = trigger_type;

        angular.forEach($scope.triggers, function(u, i) {
          if (u.id === trigger.id) {
            $scope.triggers.splice(i, 1, trigger);
          }
        });

      } else {
        var trigger = new Trigger({
          hotel: $scope.hotel_id,
          type: trigger_type.id,
          reply: reply.id
        });
        trigger.$save(function(response) {
            // Comment out: only needed for debugging
            // console.log(response);
          },
          function(err) {
            // Comment out: only needed for debugging
            // console.log(err);
          }).then(function(response) {
          response.reply = reply;
          response.type = trigger_type;
          $scope.triggers.push(response);
        });;
      }
      $scope.trigger_type = $scope.reply_trigger = null;
    }

    $scope.deleteTrigger = function(trigger) {
      angular.forEach($scope.triggers, function(u, i) {
        if (u.id === trigger.id) {
          $scope.triggers.splice(i, 1);
        }
      })

      trigger.$remove({
        id: trigger.id
      });
    }
  }
]);
