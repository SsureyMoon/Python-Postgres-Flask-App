function statusChangeCallback(response) {
    console.log('statusChangeCallback');
    // The response object is returned with a status field that lets the
    // app know the current login status of the person.
    // Full docs on the response object can be found in the documentation
    // for FB.getLoginStatus().
    if (response.status === 'connected') {
      // Logged into your app and Facebook.
        FB.api('/me', function(info){
            $.ajax({
                type: 'POST',
                url: '/auth/fconnect/',
                processData: false,
                contentType: 'application/octet-stream; charset=utf-8',
                data: JSON.stringify({
                    email: info.email,
                    name: info.name,
                    access_token: response.authResponse.accessToken
                }),
                success: function(result){
                    if(result){
                        window.location.href = "/";
                    } else if (authResult['error']){
                        console.log('There was an error: ' + authResult['error']);
                    } else {
                        $('#result').html('Failed to  make a server-side call.' +
                                'Check your configuration and console');
                    }
                },
                error: function(result){
                    var errorFlash = '<div class="alert alert-danger" role="alert">' +
				        '<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span>' +
                        'We can\'t access your facebook' + '</div>';
                    $('.flash-holder').html(errorFlash);
                }
            })
        })
    } else {
        var errorFlash = '<div class="alert alert-danger" role="alert">' +
				'<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span>' +
                'We can\'t access your facebook' + '</div>';
            $('.flash-holder').html(errorFlash);
    }
  }

// This function is called when someone finishes with the Login
  // Button.  See the onlogin handler attached to it in the sample
  // code below.
function checkLoginState() {
    FB.getLoginStatus(function(response) {
      statusChangeCallback(response);
    });
}

(function(d, s, id) {
  var js, fjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) return;
  js = d.createElement(s); js.id = id;
  js.src = "//connect.facebook.net/en_US/sdk.js#xfbml=1&version=v2.3&appId=791336444272469";
  fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));


$('a[link="logout"]').click(
    function() {
        FB.logout(function(response){});
        $.get('/gdisconnect/', function (response) {});
        $.get('/auth/logout/', function () {
        }).done(function(){
            window.location.reload(true);
        }).fail(function(){
            window.location.reload(true);
        })
    }
);