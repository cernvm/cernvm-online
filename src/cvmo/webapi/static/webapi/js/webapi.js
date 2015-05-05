
(function(window) {

	/**
	 * Launch a VM using the specified VMCP URL 
	 */
	window.launchMachine = function(vmcp_url) {

		// Initialize CernVM WebAPI
		CVM.startCVMWebAPI(function(api) {
			$("#lbl-status").text("CernVM WebAPI Ready");

			// Request a session through our specified VMCP endpoint
			api.requestSession(vmcp_url, function(session) {
				$("#lbl-status").text("Session open");
										
				// Obtained from the Appendix
				var STATE_NAMES = ['Not yet created', '', 'Powered off', 'Saved', 'Paused', 'Running'];

				// Listen for state changed events
				session.addEventListener('stateChanged', function(newState) {
					$("#lbl-status").text(STATE_NAMES[newState]);
				});

			});

		});

	}

})(window);
