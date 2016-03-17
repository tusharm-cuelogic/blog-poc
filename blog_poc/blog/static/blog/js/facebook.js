// function statusChangeCallback(response) {
//     console.log('statusChangeCallback');
//     console.log(response);
//     if (response.status === 'connected') {
//       // Logged into your app and Facebook.
//       testAPI();
//     }
//   }

//   function checkLoginState() {
//     FB.getLoginStatus(function(response) {
//       statusChangeCallback(response);
//     });
//   }

//   window.fbAsyncInit = function() {
//   FB.init({
//     appId      : '1546713182325971',
//     cookie     : true,  // enable cookies to allow the server to access 
//                         // the session
//     xfbml      : true,  // parse social plugins on this page
//     version    : 'v2.5' // use graph api version 2.5
//   });

//   FB.getLoginStatus(function(response) {
//     statusChangeCallback(response);
//   });

//   };

  // // Load the SDK asynchronously
  // (function(d, s, id) {
  //   var js, fjs = d.getElementsByTagName(s)[0];
  //   if (d.getElementById(id)) return;
  //   js = d.createElement(s); js.id = id;
  //   js.src = "//connect.facebook.net/en_US/sdk.js";
  //   fjs.parentNode.insertBefore(js, fjs);
  // }(document, 'script', 'facebook-jssdk'));

  // function testAPI() {
  //   console.log('Welcome!  Fetching your information.... ');
  //   FB.api('/me', function(response) {
  //     console.log('Successful login for: ' + response.name);
  //   });
  // }
window.fbAsyncInit = function () {
  FB.init({
      appId:'1546713182325971',
      oauth:true,
      status:true, // check login status
      cookie:true, // enable cookies to allow the server to access the session
      xfbml:true // parse XFBML
  });
};

function fb_login(strLoginId) {
  FB.getLoginStatus(function (response) {
      if (response.status === 'connected') {
          fb_logout(strLoginId);
      } else {
          FB.login(function (response) {
              if (response.authResponse) {
                  access_token = response.authResponse.accessToken; //get access token
                  user_id = response.authResponse.userID; //get FB UID
                  // fnViewFacebookPageList(access_token);
                  console.log('Welcome!!! Fetching your information ...'+access_token);
                  console.log(response.authResponse.name);
                  console.log(user_id);

                  FB.api('/me', function(response) {
                   console.log('Good to see you, ' + response.name + '.');
                   console.log(response);
                 });
              }

          }, {
              scope:'public_profile,email'
          });


      }
  })//end
}

// fb-logout
function fb_logout(strLoginId) {
  FB.logout(function (response) {
      // FB.Auth.setAuthResponse(null, 'unknown');
      fb_login(strLoginId);
  });
}// FB.log-out