document.getElementById('signupForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch('/signup/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            alert('Registration successful!');
            window.location.href = '/login/';  // Redirect to login page
        } else {
            const result = await response.json();
            alert('Error: ' + JSON.stringify(result));
        }
    } catch (error) {
        console.error('Error:', error);
    }
});

document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const phone_number = document.getElemtById('phone_number').value.trim();
    const password = document.getElementById('password').value;

    fetch('/signin/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            phone_number: phone_number,
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
