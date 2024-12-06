// Function to extract the prescription ID from the URL
const getPrescriptionIdFromUrl = () => {
    const urlSegments = window.location.pathname.split('/');
    const id = urlSegments[2]; // Get the last segment of the URL
    return parseInt(id, 10); // Convert to an integer
};

// Function to fetch prescription data
const fetchPrescription = async (id) => {
    const accessToken = localStorage.getItem('access_token'); // Get the token from local storage
    // console.log(accessToken);
    if (!accessToken) {
        document.getElementById('prescription-container').innerHTML = `
            <p class="text-red-500">Error: Access token not found. Please log in.</p>
        `;
        return;
    }

    try {
        const response = await fetch(`/patient-prescription/${id}/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`, // Include the token
            },
        });

        if (!response.ok) {
            throw new Error(`Failed to fetch prescription data: ${response.statusText}`);
        }

        const data = await response.json();
        renderPrescription(data);
    } catch (error) {
        document.getElementById('prescription-container').innerHTML = `
            <p class="text-red-500">Error: ${error.message}</p>
        `;
    }
};

// Function to render prescription data
const renderPrescription = (data) => {
    const container = document.getElementById('prescription-container');
    container.innerHTML = `
        <h2 class="font-semibold text-xl mb-4">General Information</h2>
        <p><strong>Doctor:</strong> ${data.doctor}</p>
        <p><strong>Patient:</strong> ${data.patient}</p>
        <p><strong>Appointment:</strong> ${data.appointment}</p>
        <p><strong>Diagnosis:</strong> ${data.diagnosis}</p>
        <p><strong>Prescription:</strong> ${data.prescription}</p>
        <p><strong>Treatment Date:</strong> ${data.treatment_date}</p>
        <p><strong>Follow-Up Date:</strong> ${data.follow_up_date || "N/A"}</p>
        <p><strong>Treatment Notes:</strong> ${data.treatment_notes}</p>
        <p><strong>Cost:</strong> $${parseFloat(data.cost).toFixed(2)}</p>

        <h2 class="font-semibold text-xl mt-6 mb-4">Medications</h2>
        ${data.medications.length > 0
            ? `<ul class="list-disc pl-5">
                ${data.medications
                    .map(
                        (med) =>
                            `<li>
                                <strong>${med.name}</strong> - ${med.dosage}, ${med.frequency}, ${med.duration}
                                <br><em>Notes:</em> ${med.notes || "N/A"}
                            </li>`
                    )
                    .join("")}
            </ul>`
            : "<p>No medications prescribed.</p>"}

        <h2 class="font-semibold text-xl mt-6 mb-4">Diagnosis</h2>
        ${data.tests.length > 0
            ? `<ul class="list-disc pl-5">
                ${data.tests
                    .map(
                        (test) =>
                            `<li>
                                <strong>${test.test_name}</strong> - ${test.test_description}
                                <br><em>Date:</em> ${test.test_date}, <em>Result:</em> ${test.result || "Pending"}, <em>Status:</em> ${test.status}
                            </li>`
                    )
                    .join("")}
            </ul>`
            : "<p>No tests prescribed.</p>"}
    `;
};

// Get the prescription ID from the URL and fetch data
const prescriptionId = getPrescriptionIdFromUrl();
if (!isNaN(prescriptionId)) {
    fetchPrescription(prescriptionId);
} else {
    document.getElementById('prescription-container').innerHTML = `
        <p class="text-red-500">Invalid Prescription ID</p>
    `;
}
