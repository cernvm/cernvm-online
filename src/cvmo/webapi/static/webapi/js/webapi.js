
(function(window) {

	// Helper function to update progress value
	function update_progress_value(value) {
		var percent = Number(value * 100).toFixed() + '%';
		$("#p-bar").css('width', percent);
	}

	// Callback handler to show the progress bar
	function progress_started(message) {
		update_progress_value(0.0);
	}

	// Callback handler to hide the progress bar when completed
	function progress_completed(message) {
		update_progress_value(1.0);
	}

	// Callback handler to update the progress bar
	function progress_updated(message, value) {
		$("#lbl-status").text(message);
		update_progress_value(value);
	}

	// Callback handler in case of error
	function progress_error(message) {
		$("#webapi-frame").removeClass("color-running");
		$("#webapi-frame").addClass("color-error");
		$("#lbl-header").text("An error occured");
		$("#lbl-status").text(message);
		update_progress_value(0.0);
	}

	/**
	 * Launch a VM using the specified VMCP URL 
	 */
	window.launchMachine = function(vmcp_url) {

		// Initialize CernVM WebAPI
		CVM.startCVMWebAPI(function(api) {
			$("#lbl-status").text("CernVM WebAPI Ready");

			// Bind progress listeners on the plugin instance
			api.addEventListener('started', progress_started);
			api.addEventListener('completed', progress_completed);
			api.addEventListener('progress', progress_updated);
			api.addEventListener('failed', progress_error);

			// Request a session through our specified VMCP endpoint
			api.requestSession(vmcp_url, function(session) {
				$("#lbl-status").text("Session open");
										
				// Obtained from the Appendix
				var STATE_NAMES = ['Not yet created', '', 'Powered off', 'Saved', 'Paused', 'Running'];

				// Bind progress listeners on the session instance
				session.addEventListener('started', progress_started);
				session.addEventListener('completed', progress_completed);
				session.addEventListener('progress', progress_updated);
				session.addEventListener('failed', progress_error);

				// Listen for state changed events
				session.addEventListener('stateChanged', function(newState) {
					$("#lbl-status").text(STATE_NAMES[newState]);

					// When we are running we don't need the window any more
					if (newState == 5) {
						window.close();
					}

				});

				// We just start the session the moment we get it
				session.start();

			});

		});

	}

})(window);
