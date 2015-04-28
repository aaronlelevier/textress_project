/**
 * Home controller definition
 */
define([
    './module',
    'ngAnimate'
], function(module) {
'use strict';

    module.controller('IndexCtrl', function IndexCtrl($scope, $location, Auth, User) {
        $scope.users = User.query();
    });


    module.controller('NavbarCtrl', ['$scope', 'Auth', function($scope, Auth) {
        $scope.isLoggedIn = !!Auth.getToken();
        $scope.logout = logout;

        function logout() {
            Auth.logout();
        }
    }]);


    module.controller('HomeCtrl', ['$scope', function($scope) {
        $scope.logo = "Textress";
        $scope.small_desc = "The SMS Concierge";
        $scope.exec_summary = "A better Guest Experience for your Hotel Customers";
        $scope.selling_points = [
            "Easy to use",
            "Just like texting but from a computer",
            "Automated Messages",
            "Control Panel",
            "Business Intelligence usage charts and information",
            "RESTful API",
            "Secure via SSL encyption",
            "We built this because we love the Hotel industry and Technology"
        ];

    }]);

    module.controller('FeaturesCtrl', ['$scope', function($scope) {
        $scope.logo = "Textress";
    }]);

    module.controller('PricingCtrl', ['$scope', 'Pricing', function($scope, Pricing) {
        //prices will be from a DRF REST endpoint, so when changed in the DB,
        //they are auto-reflected here
        $scope.prices = Pricing.query();

        $scope.volumes = [500, 2500, 5000, 7500];

        $scope.volume = "";
        $scope.submit_volume = function(volume) {
            $scope.volume = volume;
        }

        // calculate SMS cost
        $scope.calc_cost = function() {
            $scope.cost = 0;
            angular.forEach($scope.prices, function(p) {
                if ($scope.volume >= p.end) {
                    $scope.cost += p.price * (p.end - p.start + 1);
                } else if ($scope.volume >= p.start && $scope.volume < p.end) {
                    $scope.cost += p.price * ($scope.volume - p.start + 1);
                }
            });
            return $scope.cost;
        }

        $scope.$watch(
            'volume',
            function(newValue) {
                return newValue;
            });
    }]);

    module.controller('ContactCtrl', ['$scope', 'Contact', function($scope, Contact) {
        $scope.title = "Contact";

        //display list of contacts for testing
        $scope.contacts = Contact.query();

        // create new Contact
        $scope.submitContact = function(contact) {
            var c = new Contact({
                name: contact.name,
                email: contact.email,
                subject: contact.subject,
                message: contact.message
            });

            c.$save(function() {
                console.log("Contact Saved: ", c);
            });
        }

        // empty Object to start, and reset() to clear form
        $scope.master = {};
        $scope.reset = function() {
            $scope.contact = angular.copy($scope.master);
        };
        $scope.reset();
    }]);

    module.controller('SMSDemoCtrl', ['$scope', '$rootScope', '$http', '$timeout',
        function($scope, $rootScope, $http, $timeout) {

            // grid(0), list (1)
            $scope.layoutMode = 0;
            $scope.list = [];
            $scope.currentAnimation;
            $scope.isShow = true;
            $scope.animations = ["toggle",
                "spin-toggle",
                "scale-fade",
                "scale-fade-in",
                "bouncy-scale-in",
                "flip-in",
                "slide-left",
                "slide-right",
                "slide-top",
                "slide-down",
                "bouncy-slide-left",
                "bouncy-slide-right",
                "bouncy-slide-top",
                "bouncy-slide-down",
                "rotate-in"
            ];

            $scope.addItem = function(animation) {
                $scope.animation = animation;
                for (var i = 0; i < 6; i++) {
                    $timeout(function() {
                        $scope.list.push({
                            title: "item"
                        });
                    }, 100 * i);
                };
            }

            $scope.removeItem = function(item) {
                var index = $scope.list.indexOf(item);
                $scope.list.remove(index);
            }

            $scope.cleanList = function() {
                for (var i = 0; i < $scope.list.length; i++) {
                    $timeout(function() {
                        $scope.list.pop();
                    }, 100 * i);
                };
            }

            // Play all animation, it will auto clean item list.
            $scope.autoPlayAnimation = function(index) {
                var animation = $scope.animations[index];
                if (animation) {
                    $scope.currentAnimation = animation;
                    $scope.addItem(animation);
                    $timeout(function() {
                        $scope.cleanList();
                    }, 1000);
                    $timeout(function() {
                        $scope.autoPlayAnimation(++index);
                    }, 2000);
                } else {
                    $scope.currentAnimation = undefined;
                }
            }

            $scope.switchGridMode = function() {
                $scope.layoutMode = 0;
            }

            $scope.switchListMode = function() {
                $scope.layoutMode = 1;
            }

            $scope.toggle = function() {
                $scope.isShow = !$scope.isShow;
            }
        }]);

        Array.prototype.remove = function(from, to) {
            var rest = this.slice((to || from) + 1 || this.length);
            this.length = from < 0 ? this.length + from : from;
            return this.push.apply(this, rest);
        };

});



