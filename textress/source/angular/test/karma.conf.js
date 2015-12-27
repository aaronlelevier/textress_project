module.exports = function(config){
  config.set({

    basePath : '../',

    files : [
      '../vendor/angular/angular.js',
      '../vendor/angular-route/angular-route.js',
      '../vendor/angular-mocks/angular-mocks.js',
      '../vendor/angular-resource/angular-resource.min.js',
      '../vendor/angular-ui-router/release/angular-ui-router.min.js',
      '../angular/concierge/*.js',
      '../angular/index/*.js',
      '../angular/main/*.js',
      '../angular/config.js',
      '../angular/test/unit/**/*.js',
      '../angular/test/unit/**/**/*.js',
    ],

    autoWatch : true,

    frameworks: ['jasmine'],

    browsers : ['Firefox'],

    plugins : [
            'karma-firefox-launcher',
            'karma-jasmine'
            ],

    junitReporter : {
      outputFile: 'test_out/unit.xml',
      suite: 'unit'
    }

  });
};