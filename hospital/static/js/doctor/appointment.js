// static/js/appointment.js
document.getElementById('appointmentForm').addEventListener('submit', async function(e) {
    e.preventDefault();  // Prevent form submission
    const formData = new FormData(this);
  
    // Get doctor ID from the URL
    const doctorId = window.location.pathname.split('/').filter(Boolean).pop();  // Extracts '1' from '/appointment/1/'
  
    // Add doctor ID to the data
    formData.append('doctor', doctorId);
  
    // Convert formData to JSON
    const data = Object.fromEntries(formData.entries());
  
    try {
      const response = await fetch('/api/appointments/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
        body: JSON.stringify(data)
      });
  
      if (response.ok) {
        alert('Appointment successfully booked!');
        // window.location.reload();
      } else {
        const result = await response.json();
        alert('Error: ' + JSON.stringify(result));
      }
    } catch (error) {
      console.error('Error:', error);
      alert('An error occurred while booking the appointment.');
    }
  });
  
  // Function to get CSRF token from cookie
  function getCSRFToken() {
    const cookies = document.cookie.split('; ');
    for (const cookie of cookies) {
      const [name, value] = cookie.split('=');
      if (name === 'csrftoken') return value;
    }
    return '';
  }
  