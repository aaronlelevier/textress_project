define(['angular'], function (angular) {
  angular.module('app.ui.menu', ['ui.router'])

    .directive('menu', function () {
      return {
        replace: true,
        restrict: 'E',
        template: '<ul class="menu" ng-transclude></ul>',
        transclude: true
      };
    })

    .directive('menuI', function ($state) {
      return {
        replace: true,
        restrict: 'E',
        scope: {
          sref: '@'
        },
        templateUrl: '/source/js/modules/ui/menu/menu-item.html',
        transclude: true,
        link: function (scope) {

          function update() {
            scope.isCurrent = $state.includes(scope.sref);
            scope.isLink = !$state.is(scope.sref);
          }

          scope.$on('$stateChangeSuccess', update);
          update();
        }
      };
    });
});
