document.addEventListener('DOMContentLoaded', () => {
    const appointmentDetailsContainer = document.getElementById('appointment-details');
    const videoLinkButton = document.getElementById('video-link');

    // Replace this with the actual appointment ID (could be passed dynamically)
    const appointmentId = window.location.href.split('/')[4];
    const token = localStorage.getItem('access_token');
    // Fetch the appointment details
    fetch(`/api/appointment/${appointmentId}/`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,  // Replace with actual JWT token
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Populate appointment details
        console.log(data);
        appointmentDetailsContainer.innerHTML = `
            <p><strong>Doctor:</strong> ${data.doctor}</p>
            <p><strong>Patient Name:</strong> ${data.patient_name}</p>
            <p><strong>Phone Number:</strong> ${data.phone_number}</p>
            <p><strong>Email:</strong> ${data.email}</p>
            <p><strong>Address:</strong> ${data.address}</p>
            <p><strong>Appointment Date:</strong> ${new Date(data.appointment_date).toLocaleString()}</p>
            
        `;

        // Set video call link
        videoLinkButton.href = data.video_link;
    })
    .catch(error => {
        console.error('Error fetching appointment details:', error);
        appointmentDetailsContainer.innerHTML = `<p class="text-red-500">Failed to load appointment details. Please try again later.</p>`;
    });
});
