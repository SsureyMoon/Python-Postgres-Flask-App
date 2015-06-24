function signInCallback(authResult){
    if (authResult['code']){
        $('#signinButton').attr('style', 'display: none');
        $.ajax({
            type: 'POST',
            url: '/auth/gconnect/?_csrf_token='+csrf_token,
            processData: false,
            contentType: 'application/octet-stream; charset=utf-8',
            data: authResult['code'],
            success: function(result){
                if(result){
                    window.location.href = "/";
                } else {
                    var errorFlash = '<div class="alert alert-danger" role="alert">' +
                            '<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span>' +
                            'Error to connect goolge plus' + '</div>';
                    $('.flash-holder').html(errorFlash);
                }
            }
        })
    }
}