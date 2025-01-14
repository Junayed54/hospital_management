const dashboardApiUrl = '/api/dashboard/';
const appointmentsApiUrl = '/api/patient-appointments/';
const testOrdersApiUrl = '/api/test-orders/';  // Corrected API URL for test orders

// Fetch the access token from localStorage
const accessToken = localStorage.getItem('access_token');

if (!accessToken) {
    console.error('Access token not found in localStorage');
    // Redirect to login page or show an error message
} else {
    // Fetch dashboard data
    axios.get(dashboardApiUrl, {
        headers: {
            'Authorization': `Bearer ${accessToken}`
        }
    })
    .then(response => {
        const data = response.data;

        // Update basic patient details
        document.getElementById('gender').innerText = data.gender;
        document.getElementById('age').innerText = data.age;
        document.getElementById('bloodType').innerText = data.blood_type;

        // Populate data lists by date
        populateDataList('bpList', data.bp_levels, 'BP: Systolic/Diastolic');
        populateDataList('sugarList', data.sugar_levels, 'Sugar Level');
        populateDataList('heartRateList', data.heart_rates, 'Heart Rate');
        populateDataList('cholesterolList', data.cholesterol_levels, 'Cholesterol Level');
    })
    .catch(error => {
        console.error('Error fetching dashboard data:', error);
    });

    // Fetch test orders data
    axios.get(testOrdersApiUrl, {
        headers: {
            'Authorization': `Bearer ${accessToken}`
        }
    })
    .then(response => {
        const testOrders = response.data;  // Assuming the response contains a "test_orders" array
        console.log(testOrders);
        // Populate test order list
        populateTestList('testList', testOrders);
    })
    .catch(error => {
        console.error('Error fetching test orders data:', error);
    });

    // Fetch appointments data
    axios.get(appointmentsApiUrl, {
        headers: {
            'Authorization': `Bearer ${accessToken}`
        }
    })
    .then(response => {
        const appointments = response.data;

        // Populate upcoming appointments
        populateAppointmentsTable(
            'upcomingAppointmentsTable',
            appointments.upcoming_appointments,
            true
        );

        // Populate joined appointments
        populateAppointmentsTable(
            'joinedAppointmentsTable',
            appointments.joined_appointments,
            false
        );
    })
    .catch(error => {
        console.error('Error fetching appointments data:', error);
    });
}

// Helper function to populate test order list
// Helper function to populate test order list with download functionality
function populateTestList(listId, testOrders) {
    const list = document.getElementById(listId);
    list.innerHTML = ''; // Clear existing content

    testOrders.forEach(test => {
        const listItem = document.createElement('li');

        // Create text for the test order
        listItem.innerText = `${test.test_name}: status: ${test.status}, (Scheduled on: ${test.order_date})`;

        // Check if a result file exists
        if (test.test_result && test.test_result.result_file) {
            // Create a download button/link
            const downloadButton = document.createElement('a');
            downloadButton.href = test.test_result.result_file_url; // URL of the result file
            downloadButton.target = '_blank'; // Open in a new tab
            downloadButton.download = ''; // Enable file download
            downloadButton.innerText = 'Result';
            downloadButton.style.marginLeft = '10px'; // Add some spacing
            downloadButton.classList.add('text-red-700')

            // Append the download button to the list item
            listItem.appendChild(downloadButton);
        }

        // Append the list item to the list
        list.appendChild(listItem);
    });
}


// Helper function to populate data list (for other data like BP, Sugar, etc.)
function populateDataList(listId, items, label) {
    const list = document.getElementById(listId);
    list.innerHTML = ''; // Clear existing content
    items.forEach(item => {
        const listItem = document.createElement('li');
        listItem.innerText = `${item.date}: ${label} - ${item.systolic ? item.systolic + '/' + item.diastolic : item.level || item.rate}`;
        list.appendChild(listItem);
    });
}

// Helper function to populate appointments table
function populateAppointmentsTable(tableId, appointments, isUpcoming = false) {
    const tableBody = document.getElementById(tableId).querySelector('tbody');
    tableBody.innerHTML = ''; // Clear existing rows

    appointments.forEach(appointment => {
        const row = document.createElement('tr');

        // Add appointment details
        row.innerHTML = `
            <td>${appointment.id}</td>
            <td>${appointment.doctor}</td>
            <td>${appointment.appointment_date}</td>
            <td>${appointment.status}</td>
            <td>
                <button class="action-button" data-id="${appointment.id}">Action</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}
