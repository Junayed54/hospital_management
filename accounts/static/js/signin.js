document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();

    // Get phone number and password from the form
    const phone_number = document.getElementById('phone_number').value;
    const password = document.getElementById('password').value;

    // Send the login request to the server
    fetch('/signin/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            phone_number: phone_number,  // Send phone number instead of username
            password: password,
        }),
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw err; });  // Handle non-200 responses
        }
        return response.json();
    })
    .then(data => {
        if (data.access) {
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            alert('Login successful!');  // Optional success message
            window.location.href = '/';  // Redirect to home page on successful login
        } else {
            alert(data.detail || 'Invalid phone number or password');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert(error.detail || 'An unexpected error occurred. Please try again.');
    });
});
