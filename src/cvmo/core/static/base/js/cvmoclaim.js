
CVMO.setupClaim = function(pollURL, url) {
    var timer;

    // Check the status of an instance that pends pairing
    var checkStatus = function()
    {
        jQuery.ajax(
            {
                url: pollURL + "?rand=" + Math.round(Math.random() * 100000000),
                dataType: "json",
                success: function(data, textStatus, jqXHR)
                {
                    if (data.status == "claimed") {
                        window.location=url;
                        clearInterval(timer);
                    } else if (data.status == "pending") {
                        jQuery("#pinframe").html(
                            "<span class=\"gray\">Pending</span>"
                        );
                    } else if (data.status == "timeout") {
                        jQuery("#pinframe").html(
                            "<span class=\"red\">Expired</span>"
                        );
                        clearInterval(timer);
                    } else if (data.status == "error") {
                        jQuery("#pinframe").html(
                            "<span class=\"red\">Error</span>"
                        );
                        clearInterval(timer);
                    }
                },
                error: function(jqXHR, errorThrown)
                {
                    jQuery("#pinframe").html(
                        "<span class=\"red\">Error: " + errorThrown + "</span>"
                    );
                    clearInterval(timer);
                }
            }
        );
    }

    // Setup timer
    timer = setInterval(checkStatus, 5000);
};
