document.addEventListener('DOMContentLoaded', function() {
    var isAuthenticated = document.cookie.includes('user_authenticated=true');
    var loginButton = document.getElementById('login');
    var logoutButton = document.getElementById('logout');
    var signupButton = document.getElementById('signup');
    console.log("isAuthenticated: ",isAuthenticated)
    if (isAuthenticated) {
      loginButton.style.display = 'None';
      logoutButton.style.display = 'block';
      signupButton.style.display = 'None';
    } else {
      loginButton.style.display = 'block';
      logoutButton.style.display = 'None';
      signupButton.style.display = 'block';
    }
});