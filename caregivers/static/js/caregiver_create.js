document.getElementById('caregiverForm').addEventListener('submit', function (e) {
    e.preventDefault(); // Prevent the default form submission

    const formData = new FormData(this);

    // Convert form data to a plain object for API request
    const data = {};
    formData.forEach((value, key) => {
        data[key] = value;
    });

    // Add the department and position to the data object (for both the form and the API request)
    data['department'] = document.getElementById('department').value;
    data['position'] = document.getElementById('position').value;

    // Get the access token from local storage
    const token = localStorage.getItem('access_token');
    
    if (!token) {
        document.getElementById('error-message').classList.remove('hidden');
        document.getElementById('error-message').innerText = 'Access token not found. Please log in as admin.';
        document.getElementById('success-message').classList.add('hidden');
        return;
    }

    // Send the form data to the backend API for user and caregiver creation
    axios.post('/api/caregiver/create/', data, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
        .then((response) => {
            // Success handling
            document.getElementById('success-message').classList.remove('hidden');
            document.getElementById('success-message').innerText = 'Caregiver created successfully!';
            document.getElementById('error-message').classList.add('hidden');
        })
        .catch((error) => {
            // Error handling
            document.getElementById('error-message').classList.remove('hidden');
            document.getElementById('error-message').innerText = error.response ? error.response.data.error : 'Something went wrong!';
            document.getElementById('success-message').classList.add('hidden');
        });
});


document.addEventListener('DOMContentLoaded', function () {
    const departmentSelect = document.getElementById('department');
    const accessToken = localStorage.getItem('access_token') || 'your_access_token';

    // Fetch departments from the API
    axios.get('/api/departments/', {
        headers: {
            'Authorization': `Bearer ${accessToken}`
        }
    })
        .then(response => {
            const departments = response.data; // Assuming the API returns a list of department objects
            departments.forEach(department => {
                const option = document.createElement('option');
                option.value = department.id; // Replace `id` with the actual field used for the department identifier
                option.textContent = department.name; // Replace `name` with the field that contains the department's name
                departmentSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error fetching departments:', error);
            const errorMessage = document.getElementById('error-message');
            errorMessage.textContent = 'Failed to load departments. Please try again later.';
            errorMessage.classList.remove('hidden');
        });
});
