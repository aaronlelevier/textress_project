if (typeof define !== 'function') {
  // to be able to require file from node
  var define = require('amdefine')(module);
}

define({
  baseUrl: '/static/',

  paths: {
    'angular'       : 'vendor/angular/angular.min',
    'jquery'        : 'vendor/jquery/dist/jquery.min',
    'ngResource'    : 'vendor/angular-resource/angular-resource.min',
    'ui.router'     : 'vendor/angular-ui-router/release/angular-ui-router.min',
    'ng.django.forms': 'forms/js/ng-django-forms',

  },

    shim: {
        'angular': {
            'deps': ['jquery'],
            'exports': 'angular'
        },
        'ngResource': ['angular'],
        'ui.router': ['angular'],
        'ng.django.forms': ['angular'],
    }
});


