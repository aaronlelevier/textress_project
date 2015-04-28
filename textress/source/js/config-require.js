if (typeof define !== 'function') {
  // to be able to require file from node
  var define = require('amdefine')(module);
}

define({
  baseUrl: '/source/',

  paths: {
    'angular'       : 'vendor/angular/angular.min',
    // 'async'         : 'vendor/requirejs-plugins/src/async',  //Not currently installed
    'jquery'        : 'vendor/jquery/dist/jquery.min',
    'ngResource'    : 'vendor/angular-resource/angular-resource.min',
    'ngAnimate'     : 'vendor/angular-animate/angular-animate.min',
    'ui.router'     : 'vendor/angular-ui-router/release/angular-ui-router.min',
    'ui.bootstrap'  : 'vendor/angular-ui-bootstrap/ui-bootstrap.min',
    'angular.filter': 'vendor/angular-filter/dist/angular-filter.min'
  },

  shim: {
    'angular': {
      'deps': ['jquery'],
      'exports': 'angular'
    },
    'ngResource': ['angular'],
    'ngAnimate' : ['angular'],
    'ui.router' : ['angular'],
    'ui.bootstrap': ['angular'],
    'angular.filter' : ['angular']
  }
});
