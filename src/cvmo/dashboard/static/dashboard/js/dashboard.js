jQuery(
    function()
    {
        /* Tooltips */
        jQuery("*[data-toggle=\"tooltip\"]").tooltip();

        /* Remote modals */
        jQuery("*[data-toggle=\"remote-modal\"]").remoteModal();

        /* WebAPI */
        jQuery("a.webapi-deploy-handle").click(
            function(e)
            {
                e.preventDefault();

                /* Get config index */
                var context_id = jQuery(this).data("context-id"),
                    config_index = jQuery(this).data("config-index");

                /* Prepare the URL to query */
                var url = 'http://cernvm-online.cern.ch';
                if (String(window.location).indexOf("devel") != -1)
                    url += "/devel";
                url += "/webapi/req?context="+ context_id +"&config=" + config_index;

                /* Open an [HTTP] window to handle this request */
                var win_w = 700,
                    win_h = 500,
                    win = window.open(url, "webapi_popup", 
                         "width=" + win_w
                      + ",height=" + win_h
                      + ",left=" + ((window.screen.width - win_w) / 2)
                      + ",top=" + ((window.screen.height - win_h) / 2)
                      + ",location=no"
                      + ",menubar=no"
                      + ",resizable=no"
                      + ",scrollbars=no"
                      + ",titlebar=no"
                      + ",toolbar=no"
                    );

            }
        );
    }
);
