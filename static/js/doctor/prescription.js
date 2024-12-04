document.getElementById('prescription-form').addEventListener('submit', async function(event) {
    event.preventDefault();  // Prevent default form submission

    // Retrieve form values
    const diagnosis = document.getElementById('diagnosis').value.trim();
    const prescription = document.getElementById('prescription').value.trim();
    const treatmentDate = document.getElementById('treatment_date').value;
    const followUpDate = document.getElementById('follow_up_date').value;
    const treatmentNotes = document.getElementById('treatment_notes').value.trim();

    // Extract patientId and doctorId from URL query parameters
    const urlParams = new URLSearchParams(window.location.search);
    const appointmentId = urlParams.get('appointment_id');  // Corrected spelling from "appoinment_id" to "appointment_id"
    const doctorId = urlParams.get('doctor_id');    // Extracts the doctor_id parameter
    console.log("ids: " , doctorId, appointmentId); //
    if (!appointmentId || !doctorId) {
        alert('Missing appointment or doctor information in URL.');
        return;  // Stop execution if IDs are missing
    }

    try {
        const response = await fetch('/prescriptions/', {  // Adjust this endpoint to match your Django view
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem('access_token')  // JWT for secure authentication
            },
            body: JSON.stringify({
                doctor: doctorId,
                appointment: appointmentId,  // Corrected key name from "appoinment" to "appointment"
                diagnosis: diagnosis,
                prescription: prescription,
                treatment_date: treatmentDate,
                follow_up_date: followUpDate,
                treatment_notes: treatmentNotes
            })
        });

        if (response.ok) {
            const data = await response.json();
            alert('Prescription submitted successfully!');
            window.location.href = '/';  // Redirect to the appropriate page after submission
        } else {
            const errorData = await response.json();
            alert('Error: ' + (errorData.detail || 'Failed to submit prescription.'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An unexpected error occurred. Please try again later.');
    }
});
