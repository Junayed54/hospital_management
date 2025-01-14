document.addEventListener('DOMContentLoaded', function () {
    const departmentId = window.location.pathname.split('/')[2]; // Extract the department ID from the URL
    const token = localStorage.getItem('access_token'); // Get token from local storage

    if (!token) {
        alert('Access token not found. Please log in.');
        return;
    }

    fetch(`/api/departments/${departmentId}/`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    })
        .then(response => {
            if (!response.ok) {
                // Handle permission denied or other errors
                if (response.status === 403) {
                    return response.json().then(data => {
                        throw new Error(data.detail || 'Permission Denied');
                    });
                }
                throw new Error('Failed to fetch department details');
            }
            return response.json();
        })
        .then(data => {
            
            // Populate department details
            document.getElementById('department-name').innerText = data.department.name;
            document.getElementById('department-description').innerText = data.department.description || 'No description available';

            // Populate users list
            const usersList = document.getElementById('users-list');
            usersList.innerHTML = ''; // Clear any previous content

            data.users.forEach(user => {
                // Create a user card
                const userCard = document.createElement('div');
                userCard.className = 'bg-white p-4 rounded-lg shadow-md border mb-4';

                const phoneNumber = document.createElement('h3');
                phoneNumber.className = 'text-lg font-semibold mb-2';
                phoneNumber.innerText = `Phone: ${user.phone_number}`;

                const email = document.createElement('p');
                email.className = 'text-gray-700';
                email.innerText = `Email: ${user.email || 'N/A'}`;

                const position = document.createElement('p');
                position.className = 'text-gray-700';
                position.innerText = `Position: ${user.position || 'Not Assigned'}`;

                const role = document.createElement('p');
                role.className = 'text-gray-700';
                role.innerText = `Role: ${user.role}`;

                const gender = document.createElement('p');
                gender.className = 'text-gray-700';
                gender.innerText = `Gender: ${user.gender || 'N/A'}`;

                // Append details to user card
                userCard.appendChild(phoneNumber);
                userCard.appendChild(email);
                userCard.appendChild(position);
                userCard.appendChild(role);
                userCard.appendChild(gender);

                // Append card to the list
                usersList.appendChild(userCard);
            });
        })
        .catch(error => {
            console.error('Error fetching department details:', error);
            alert(error.message); // Show the error message
        });
});
