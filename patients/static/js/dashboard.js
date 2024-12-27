// API URLs
const dashboardApiUrl = '/api/dashboard/';
const appointmentsApiUrl = '/api/patient-appointments';

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
        populateDataList('bpList', data.bp_levels, 'BP: Systolic');
        populateDataList('sugarList', data.sugar_levels, 'Sugar Level');
        populateDataList('heartRateList', data.heart_rates, 'Heart Rate');
        populateDataList('cholesterolList', data.cholesterol_levels, 'Cholesterol Level');
    })
    .catch(error => {
        console.error('Error fetching dashboard data:', error);
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

// Helper function to populate appointments table
function populateAppointmentsTable(tableId, appointments) {
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

// Helper functions
function populateDataList(listId, items, label) {
    
    const list = document.getElementById(listId);
    list.innerHTML = ''; // Clear existing content
    items.forEach(item => {
        const listItem = document.createElement('li');
        listItem.innerText = `${item.date}: ${label} - ${item.level || item.systolic || item.rate}`;
        list.appendChild(listItem);
    });
}

function populateAppointmentsTable(tableId, appointments, isUpcoming = false) {
    const tableBody = document.getElementById(tableId).getElementsByTagName('tbody')[0];
    tableBody.innerHTML = ''; // Clear existing content

    appointments.forEach(appointment => {
        const row = tableBody.insertRow();

        // Add appointment details
        row.insertCell(0).innerText = appointment.patient_name;
        row.insertCell(1).innerText = appointment.doctor.name;
        row.insertCell(2).innerText = new Date(appointment.appointment_date).toLocaleString();
        row.insertCell(3).innerText = appointment.status;

        // Add action buttons for upcoming appointments
        const actionCell = row.insertCell(4);
        if (isUpcoming) {
            actionCell.innerHTML = `
                <a href="/appointment_details/${appointment.id}/" class="btn btn-primary">View</a>

                
                <button class="btn btn-danger" onclick="cancelAppointment('${ appointment.id }')">Cancel</button>
            `;
        } else {
            actionCell.innerHTML = '<span>No Actions Available</span>';
        }
    });
}

function cancelAppointment(appointmentId) {
    if (confirm('Are you sure you want to cancel this appointment?')) {
        fetch(`/appointments/${appointmentId}/cancel/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}` // Include token if required
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);
                location.reload(); // Refresh to update the status
            } else {
                alert(data.error || 'An error occurred.');
            }
        });
    }
}
function viewAppointment(appointmentId) {
    alert(`Viewing appointment ${appointmentId}`);
    // Redirect or open a modal for viewing the appointment
}

function joinAppointment(appointmentId) {
    alert(`Joining appointment ${appointmentId}`);
    // Implement the logic to join the appointment (e.g., open video link)
}

// function cancelAppointment(appointmentId) {
//     alert(`Canceling appointment ${appointmentId}`);
//     // Implement the logic to cancel the appointment
// }
