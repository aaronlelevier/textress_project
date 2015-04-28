define([
    './module'
], function(module) {
    'use strict';

    module.directive('myHello',
        function() {
            return ({
                template: '<link rel="stylesheet" href="/source/vendor/bootstrap/dist/css/bootstrap.min.css">' +
                          '<style type="text/css">h4 {color:grey;}</style>'
            });
        });
});