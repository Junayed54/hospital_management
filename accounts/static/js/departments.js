document.addEventListener('DOMContentLoaded', function() {
    // Function to fetch departments and render them in cards
    function fetchDepartments() {
        const token = localStorage.getItem('access_token'); // Get token from localStorage
        
        if (!token) {
            alert('You are not logged in. Please log in to view departments.');
            return;
        }

        axios.get('/api/departments/', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => {
            const departments = response.data; // Assume the API returns a list of departments
            renderDepartments(departments);
        })
        .catch(error => {
            console.error('Error fetching departments:', error.message);
            alert(error.message);
        });
    }

    // Function to render the departments in cards
    function renderDepartments(departments) {
        const departmentsList = document.getElementById('departments-list');
        departmentsList.innerHTML = ''; // Clear any previous content
    
        departments.forEach(department => {
            // Create a department card
            const card = document.createElement('div');
            card.className = 'bg-white p-6 rounded-lg shadow-md border cursor-pointer'; // Add cursor pointer for clickable
    
            const title = document.createElement('h3');
            title.className = 'text-xl font-semibold mb-2';
            title.innerText = department.name;
    
            const description = document.createElement('p');
            description.className = 'text-gray-700 mb-4';
            description.innerText = department.description || 'No description available';
    
            // Create a button to view positions in the department
            
    
            // Wrap the entire card in an anchor tag to make it a link
            const link = document.createElement('a');
            link.href = `/departments/${department.id}/`;  // Link to the department details page
            link.className = 'block';  // Makes sure the link wraps the whole card
            link.appendChild(card);
    
            // Append elements to the card
            card.appendChild(title);
            card.appendChild(description);
            
    
            // Append the link (which wraps the card) to the list
            departmentsList.appendChild(link);
        });
    }
    

    // Fetch departments on page load
    fetchDepartments();
});
