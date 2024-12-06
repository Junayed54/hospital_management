// appointments.js

// Function to fetch appointments from the API
async function fetchAppointments() {
    const appointmentsContainer = document.getElementById('appointments-container');
    const loadingSpinner = document.getElementById('loading');

    // Show loading spinner while fetching
    loadingSpinner.classList.remove('hidden');

    try {
        // Fetch data from the API using the fetch() method
        const response = await fetch('/patient-appointment/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem('access_token') // Use JWT token for authentication
            }
        });

        // Hide loading spinner
        loadingSpinner.classList.add('hidden');

        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }

        const data = await response.json();

        // Access the results array from the API response
        const appointments = data.results || [];

        if (appointments.length === 0) {
            appointmentsContainer.innerHTML = '<p class="text-center text-gray-500">No appointments found.</p>';
        } else {
            // Render the appointments
            appointments.forEach(appointment => {
                const appointmentElement = document.createElement('div');
                appointmentElement.classList.add('bg-white', 'shadow-md', 'rounded', 'p-4', 'mb-4');
            
                const appointmentContent = `
                    <h3 class="font-semibold text-xl">${appointment.patient_name} - ${new Date(appointment.appointment_date).toLocaleString()}</h3>
                    <p class="text-sm text-gray-600">Doctor: ${appointment.doctor || 'N/A'}</p>
                    <p class="text-sm text-gray-600">Problem: ${appointment.patient_problem || 'N/A'}</p>
                    <p class="text-sm text-gray-600">Phone: ${appointment.phone_number}</p>
                    <p class="text-sm text-gray-600">Email: ${appointment.email || 'N/A'}</p>
                    <p class="text-sm text-gray-600">Address: ${appointment.address || 'N/A'}</p>
                    ${appointment.video_link ? `<p class="text-sm text-blue-600"><a href="${appointment.video_link}" target="_blank">Video Link</a></p>` : ''}
                    <button
                        onclick="window.location.href='/patient_prescription/${appointment.id}/'"
                        class="bg-blue-500 text-white px-4 py-2 mt-2 rounded hover:bg-blue-600">
                        View Prescription
                    </button>
                `;
                appointmentElement.innerHTML = appointmentContent;
            
                appointmentsContainer.appendChild(appointmentElement);
            });
            
        }
    } catch (error) {
        console.error('Error fetching appointments:', error);
        appointmentsContainer.innerHTML = '<p class="text-center text-red-500">Failed to load appointments. Please try again later.</p>';
    }
}

// Fetch appointments when the page loads
document.addEventListener('DOMContentLoaded', function() {
    fetchAppointments();
});
