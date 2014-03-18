function makeRandomString(length)
{
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    for( var i=0; i < length; i++ )
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    return text;
}

jQuery(
    function()
    {
        /* Tooltips */
        jQuery("*[data-toggle=\"tooltip\"").tooltip();

        /* WebAPI */
        jQuery("a.webapi-deploy-handle").click(
            function(e)
            {
                e.preventDefault();
                /* Parse the request */
                var request = {
                    "contextId": jQuery(this).data("context-id"),
                    "name": jQuery(this).data("name"),
                    "memory": jQuery(this).data("memory"),
                    "CPUs": jQuery(this).data("cpus"),
                    "diskSize": jQuery(this).data("disk-size")
                };
                console.log(request);

                /* Validate the request */
                // TODO

                /* Start the VM with the CernVM Web API */
                CVM.startCVMWebAPI(
                    function(plugin)
                    {
                        var randomString = makeRandomString(5);
                        var url = "https://cernvm-online.cern.ch/vmcp/sign.php?contextualization_key="
                            + encodeURIComponent(request["contextId"])
                            + "&name=" + encodeURIComponent(request["name"]
                                            + " " + randomString)
                            + "&cpus=" + encodeURIComponent(request["CPUs"])
                            + "&ram=" + encodeURIComponent(request["memory"])
                            + "&disk=" + encodeURIComponent(request["diskSize"]);
                        plugin.requestSession(
                            url,
                            function(session)
                            {
                                session.start();
                            },
                            function(failure)
                            {
                                alert("Failed to create session: "
                                      + failure);
                            }
                        );
                    },
                    true // Let the plugin initialize the environment
                );
            }
        );
    }
);
