// // Ensure the document is ready before attaching events
// window.addEventListener('DOMContentLoaded', () => {
//     const form = document.getElementById('prescription-form');
//     const addMedicationBtn = document.getElementById('add-medication-btn');
//     const addTestBtn = document.getElementById('add-test-btn');
//     const medicationsContainer = document.getElementById('medications-container');
//     const testsContainer = document.getElementById('tests-container');

//     // Add medication item
//     addMedicationBtn.addEventListener('click', () => {
//         const item = medicationsContainer.querySelector('.medication-item').cloneNode(true);
//         resetInputs(item);
//         medicationsContainer.appendChild(item);
//     });

//     // Add test item
//     addTestBtn.addEventListener('click', () => {
//         const item = testsContainer.querySelector('.test-item').cloneNode(true);
//         resetInputs(item);
//         testsContainer.appendChild(item);
//     });

//     // Remove medication or test item
//     medicationsContainer.addEventListener('click', (e) => {
//         if (e.target.classList.contains('remove-medication-btn')) {
//             e.target.closest('.medication-item').remove();
//         }
//     });

//     testsContainer.addEventListener('click', (e) => {
//         if (e.target.classList.contains('remove-test-btn')) {
//             e.target.closest('.test-item').remove();
//         }
//     });

//     // Form submission
//     form.addEventListener('submit', async (event) => {
//         event.preventDefault();

//         const token = localStorage.getItem('access_token');
//         if (!token) {
//             alert('Authentication token is missing. Please log in again.');
//             return;
//         }

//         const formData = new FormData(form);

//         // Extract medications and tests
//         const medications = extractDynamicData(medicationsContainer, ['name[]', 'dosage[]', 'frequency[]', 'duration[]', 'notes[]']);
//         const tests = extractDynamicData(testsContainer, ['test_name[]', 'test_description[]', 'test_date[]']);
//         const urlParams = new URLSearchParams(window.location.search);
//         const appointmentId = urlParams.get('appointment_id');
//         const doctorId = urlParams.get('doctor_id');

//         if (!appointmentId || !doctorId) {
//             alert('Missing appointment or doctor information in URL.');
//             return;  // Stop execution if IDs are missing
//         }
//         // Compile data
//         const data = {
//             doctor:doctorId,
//             appointment: appointmentId,
//             diagnosis: formData.get('diagnosis'),
//             prescription: formData.get('prescription'),
//             treatment_date: formData.get('treatment_date'),
//             follow_up_date: formData.get('follow_up_date'),
//             treatment_notes: formData.get('treatment_notes'),
//             vitals: {
//                 bp_systolic: formData.get('bp_systolic'),
//                 bp_diastolic: formData.get('bp_diastolic'),
//                 sugar_level: formData.get('sugar_level'),
//                 heart_rate: formData.get('heart_rate'),
//                 cholesterol_level: formData.get('cholesterol_level')
//             },
//             medications,
//             tests
//         };
//         console.log(data);

//         try {
//             const response = await fetch('/prescriptions/', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                     'Authorization': `Bearer ${token}`
//                 },
//                 body: JSON.stringify(data)
//             });
//             console.log(response);

//             if (!response.ok) {
//                 throw new Error('Failed to submit prescription. Please try again.');
//             }

//             const result = await response.json();
//             alert('Prescription submitted successfully!');
//             window.location.href = '/';
//         } catch (error) {
//             console.error(error);
//             alert(error.message);
//         }
//     });

//     // Helper functions

//     function resetInputs(container) {
//         container.querySelectorAll('input, textarea').forEach(input => input.value = '');
//     }

//     function extractDynamicData(container, fields) {
//         const items = [];

//         container.querySelectorAll(':scope > div').forEach(item => {
//             const data = {};
//             fields.forEach(field => {
//                 const input = item.querySelector(`[name="${field}"]`);
//                 if (input) {
//                     data[field.replace('[]', '')] = input.value.trim();
//                 }
//             });
//             if (Object.keys(data).length > 0) {
//                 items.push(data);
//             }
//         });

//         return items;
//     }
// });
document.getElementById('prescription-form').addEventListener('submit', async function (event) {
    event.preventDefault(); // Prevent default form submission

    // Retrieve form values
    const diagnosis = document.getElementById('diagnosis').value.trim();
    const prescription = document.getElementById('prescription').value.trim();
    const treatmentDate = document.getElementById('treatment_date').value;
    const followUpDate = document.getElementById('follow_up_date').value;
    const treatmentNotes = document.getElementById('treatment_notes').value.trim();

    // Retrieve vital measurements
    const bpSystolic = document.getElementById('bp-systolic').value;
    const bpDiastolic = document.getElementById('bp-diastolic').value;
    const sugarLevel = document.getElementById('sugar-level').value;
    const heartRate = document.getElementById('heart-rate').value;
    const cholesterolLevel = document.getElementById('cholesterol-level').value;

    console.log(bpDiastolic, bpSystolic, sugarLevel, heartRate, cholesterolLevel);
    // Extract medications dynamically
    const medications = [];
    document.querySelectorAll('.medication-item').forEach((item) => {
        const name = item.querySelector('input[name="medication_name[]"]').value.trim();
        const dosage = item.querySelector('input[name="dosage[]"]').value.trim();
        const frequency = item.querySelector('input[name="frequency[]"]').value.trim();
        const duration = item.querySelector('input[name="duration[]"]').value.trim();
        const notes = item.querySelector('textarea[name="notes[]"]').value.trim();

        if (name && dosage && frequency && duration) {
            medications.push({ name, dosage, frequency, duration, notes });
        }
    });

    // Extract tests dynamically
    const tests = [];
    document.querySelectorAll('.test-item').forEach((item) => {
        const testName = item.querySelector('input[name="test_name[]"]').value.trim();
        const testDescription = item.querySelector('textarea[name="test_description[]"]').value.trim();
        const testDate = item.querySelector('input[name="test_date[]"]').value;

        if (testName && testDate) {
            tests.push({ testName, testDescription, testDate });
        }
    });

    // Extract patientId and doctorId from URL query parameters
    const urlParams = new URLSearchParams(window.location.search);
    const appointmentId = urlParams.get('appointment_id');
    const doctorId = urlParams.get('doctor_id');

    if (!appointmentId || !doctorId) {
        alert('Missing appointment or doctor information in URL.');
        return; // Stop execution if IDs are missing
    }

    try {
        const response = await fetch('/prescriptions/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem('access_token') // JWT authentication
            },
            body: JSON.stringify({
                doctor: doctorId,
                appointment: appointmentId,
                diagnosis,
                prescription,
                treatment_date: treatmentDate,
                follow_up_date: followUpDate,
                treatment_notes: treatmentNotes,
                vital_measurements: {
                    bp_systolic: bpSystolic,
                    bp_diastolic: bpDiastolic,
                    sugar_level: sugarLevel,
                    heart_rate: heartRate,
                    cholesterol_level: cholesterolLevel
                },
                medications, // Include medication array
                tests // Include test array
            })
        });

        if (response.ok) {
            const data = await response.json();
            alert('Prescription submitted successfully!');
            window.location.href = '/'; // Redirect after submission
        } else {
            const errorData = await response.json();
            alert('Error: ' + (errorData.detail || 'Failed to submit prescription.'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An unexpected error occurred. Please try again later.');
    }
});

// Event listener for adding medications
document.getElementById('add-medication-btn').addEventListener('click', () => {
    const container = document.getElementById('medications-container');
    const item = container.querySelector('.medication-item').cloneNode(true);
    container.appendChild(item);
});

// Event listener for adding tests
document.getElementById('add-test-btn').addEventListener('click', () => {
    const container = document.getElementById('tests-container');
    const item = container.querySelector('.test-item').cloneNode(true);
    container.appendChild(item);
});

// Event listener for removing medications
document.getElementById('medications-container').addEventListener('click', (e) => {
    if (e.target.classList.contains('remove-medication-btn')) {
        e.target.parentElement.remove();
    }
});

// Event listener for removing tests
document.getElementById('tests-container').addEventListener('click', (e) => {
    if (e.target.classList.contains('remove-test-btn')) {
        e.target.parentElement.remove();
    }
});
