document.getElementById('prescription-form').addEventListener('submit', async function(event) {
    event.preventDefault();  // Prevent default form submission

    // Retrieve form values
    const diagnosis = document.getElementById('diagnosis').value.trim();
    const prescription = document.getElementById('prescription').value.trim();
    const treatmentDate = document.getElementById('treatment_date').value;
    const followUpDate = document.getElementById('follow_up_date').value;
    const treatmentNotes = document.getElementById('treatment_notes').value.trim();

    // Extract medications dynamically
    const medications = [];
    document.querySelectorAll('.medication-item').forEach((item) => {
        const name = item.querySelector('input[name="medication_name[]"]').value.trim();
        const dosage = item.querySelector('input[name="dosage[]"]').value.trim();
        const frequency = item.querySelector('input[name="frequency[]"]').value.trim();
        const duration = item.querySelector('input[name="duration[]"]').value.trim();
        const notes = item.querySelector('textarea[name="notes[]"]').value.trim();

        if (name && dosage && frequency && duration) {  // Validate mandatory fields
            medications.push({ name, dosage, frequency, duration, notes });
        }
    });

    // Extract tests dynamically
    const tests = [];
    document.querySelectorAll('.test-item').forEach((item) => {
        const testName = item.querySelector('input[name="test_name[]"]').value.trim();
        const testDescription = item.querySelector('textarea[name="test_description[]"]').value.trim();
        const testDate = item.querySelector('input[name="test_date[]"]').value;

        if (testName && testDate) {  // Validate mandatory fields
            tests.push({ testName, testDescription, testDate });
        }
    });

    // Extract patientId and doctorId from URL query parameters
    const urlParams = new URLSearchParams(window.location.search);
    const appointmentId = urlParams.get('appointment_id');
    const doctorId = urlParams.get('doctor_id');

    if (!appointmentId || !doctorId) {
        alert('Missing appointment or doctor information in URL.');
        return;  // Stop execution if IDs are missing
    }

    try {
        const response = await fetch('/prescriptions/', {  // Adjust endpoint to match your Django view
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem('access_token')  // JWT for secure authentication
            },
            body: JSON.stringify({
                doctor: doctorId,
                appointment: appointmentId,
                diagnosis,
                prescription,
                treatment_date: treatmentDate,
                follow_up_date: followUpDate,
                treatment_notes: treatmentNotes,
                medications,  // Include medication array
                tests  // Include test array
            })
        });

        if (response.ok) {
            const data = await response.json();
            alert('Prescription and tests submitted successfully!');
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
