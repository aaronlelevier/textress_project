// var FormWizard = function() {
// 	var wizardContent = $('#wizard');
// 	var wizardForm = $('#form');
// 	var initWizard = function() {
// 		// function to initiate Wizard Form
// 		wizardContent.smartWizard({
// 			selected : 0,
// 			keyNavigation : false,
// 			onLeaveStep : leaveAStepCallback,
// 			onShowStep : onShowStep,
// 		});
// 		var numberOfSteps = 0;
// 		animateBar();
// 	};
// 	var animateBar = function(val) {
// 		if (( typeof val == 'undefined') || val == "") {
// 			val = 1;
// 		};
// 		numberOfSteps = $('.swMain > ul > li').length;
// 		var valueNow = Math.floor(100 / numberOfSteps * val);
// 		$('.step-bar').css('width', valueNow + '%');
// 	};
// 	return {
// 		init : function() {
// 			initWizard();
// 		}
// 	};
// }();
