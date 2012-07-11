
CVMO.setupClaim = function(poll_url, url) {
    var timer=0;
    // Check the status of an instance that pends pairing
    var checkStatus = function() {
        var jsonRequest = new Request.JSON({url: poll_url+'?rand='+Math.round(Math.random()*100000000), onSuccess: function(status){
            window.console.log(status);
            if (status.status == 'claimed') {
                window.location=url;
                clearInterval(expired);
            } else if (status.status == 'pending') {
                $('pinframe').set('html','<span class="gray">Pending</span>');
            } else if (status.status == 'timeout') {
                $('pinframe').set('html','<span class="red">Expired</span>');
                clearInterval(expired);
            } else if (status.status == 'error') {
                $('pinframe').set('html','<span class="red">Error</span>');
                clearInterval(expired);
            }
        }}).get();
    }
    
    // Setup timer
    timer = setInterval(checkStatus,5000);
    
};
