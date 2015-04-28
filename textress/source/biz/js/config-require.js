if (typeof define !== 'function') {
  // to be able to require file from node
  var define = require('amdefine')(module);
}

define({
  baseUrl: '/source/',

  paths: {
    'angular'       : 'vendor/angular/angular.min',
    'jquery'        : 'vendor/jquery/dist/jquery.min',
    'ngResource'    : 'vendor/angular-resource/angular-resource.min',
    'ui.router'     : 'vendor/angular-ui-router/release/angular-ui-router.min',
    'ng.django.forms': 'forms/js/ng-django-forms',

    //main-biz deps
    'bootstrap' : 'clip-one/assets/plugins/bootstrap/js/bootstrap.min',
    'jquery.transit' : 'clip-one/assets/plugins/jquery.transit/jquery.transit',
    'bootstrap-hover-dropdown' : 'clip-one/assets/plugins/hover-dropdown/twitter-bootstrap-hover-dropdown.min',
    'jquery.appear' : 'clip-one/assets/plugins/jquery.appear/jquery.appear',
    'jquery.blockUI' : 'clip-one/assets/plugins/blockUI/jquery.blockUI',
    'jquery.cookie' : 'clip-one/assets/plugins/jquery-cookie/jquery.cookie',

    //index-biz deps
    'jquery.themepunch.plugins' : 'clip-one/assets/plugins/revolution_slider/rs-plugin/js/jquery.themepunch.plugins.min',
    'jquery.themepunch.revolution' : 'clip-one/assets/plugins/revolution_slider/rs-plugin/js/jquery.themepunch.revolution.min',
    'jquery.flexslider' : 'clip-one/assets/plugins/flex-slider/jquery.flexslider',
    'jquery.stellar' : 'clip-one/assets/plugins/stellar.js/jquery.stellar.min',
    'jquery.colorbox' : 'clip-one/assets/plugins/colorbox/jquery.colorbox-min',

    //gmaps
    'gmaps' : 'clip-one/assets/plugins/gmaps/gmaps'

  },

  shim: {
    'angular': {
      'deps': ['jquery'],
      'exports': 'angular'
    },
    'ngResource': ['angular'],
    'ui.router' : ['angular'],
    'ng.django.forms' : ['angular'],

    //main-biz deps
    'bootstrap' : ['jquery'],
    'jquery.transit' : ['jquery'],
    'bootstrap-hover-dropdown' : ['jquery'],
    'jquery.appear' : ['jquery'],
    'jquery.blockUI' : ['jquery'],
    'jquery.cookie' : ['jquery'],

    //index-biz deps
    'jquery.themepunch.plugins' : ['jquery'],
    'jquery.themepunch.revolution' : ['jquery'],
    'jquery.flexslider' : ['jquery'],
    'jquery.stellar' : ['jquery'],
    'jquery.colorbox' : ['jquery'],
    'gmaps' : ['jquery']

  }
});


