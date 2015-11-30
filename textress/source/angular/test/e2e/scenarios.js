'use strict';

/* http://docs.angularjs.org/guide/dev_guide.e2e-testing */

describe('PhoneCat App', function() {

  describe('Phone list view', function() {

    beforeEach(function() {
      browser.get('../templates/frontend/index.html');
    });


    it('should filter the phone list as a user types into the search box', function() {

      expect(1).toBe(2);
      
    });
  });
});
