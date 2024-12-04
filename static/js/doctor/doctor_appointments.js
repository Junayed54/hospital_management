// static/js/appointments.js
document.addEventListener('DOMContentLoaded', async function() {
  const doctorId = window.location.pathname.split('/').filter(Boolean).pop();  // Extract doctor_id from URL
  const appointmentsList = document.getElementById('appointmentsList');

  try {
      const response = await fetch(`/api/doctor/${doctorId}/appointments/`, {
          method: 'GET',
          headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCSRFToken()  // Ensure CSRF token is included for security
          }
      });

      if (response.ok) {
          const appointments = await response.json();
          console.log(appointments);
          
          if (appointments.length === 0) {
              appointmentsList.innerHTML = '<p class="text-gray-600 text-center">No appointments available.</p>';
          } else {
              appointmentsList.innerHTML = appointments.map(appointment => `
                  <div class="bg-white shadow-lg rounded-lg p-6 mb-4">
                      <h2 class="text-2xl font-semibold">${appointment.patient_name}</h2>
                      <p class="text-gray-700"><strong>Phone:</strong> ${appointment.phone_number}</p>
                      <p class="text-gray-700"><strong>Email:</strong> ${appointment.email || 'N/A'}</p>
                      <p class="text-gray-700"><strong>Address:</strong> ${appointment.address || 'N/A'}</p>
                      <p class="text-gray-700"><strong>Date:</strong> ${new Date(appointment.appointment_date).toLocaleString()}</p>
                      
                      <!-- Prescription Button -->
                      <button class="bg-blue-500 text-white py-2 px-4 rounded mt-4 hover:bg-blue-600" 
                              onclick="prescribePatient(${appointment.id}, '${appointment.doctor}')">
                          Create Prescription
                      </button>
                      <a href="/appointment_details/${appointment.id}/" class="bg-blue-500 text-white py-2 px-4 rounded mt-4 hover:bg-blue-600" >details</a>
                  </div>
                  
              `).join('');
          }
      } else {
          appointmentsList.innerHTML = '<p class="text-red-600 text-center">Failed to load appointments. Please try again later.</p>';
      }
  } catch (error) {
      console.error('Error fetching appointments:', error);
      appointmentsList.innerHTML = '<p class="text-red-600 text-center">An unexpected error occurred. Please check your connection.</p>';
  }

  // CSRF Token function
  function getCSRFToken() {
      const cookies = document.cookie.split('; ');
      for (const cookie of cookies) {
          const [name, value] = cookie.split('=');
          if (name === 'csrftoken') return value;
      }
      return '';
  }
});

// Function to redirect for creating a prescription
function prescribePatient(appointmentId, doctor_id) {
    window.location.href = `/prescribe/?doctor_id=${encodeURIComponent(doctor_id)}&appointment_id=${encodeURIComponent(appointmentId)}`;
}
  
