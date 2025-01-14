document.getElementById('careRequestForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    // Collect form data
    const start_date = document.getElementById('start_date').value;
    const end_date = document.getElementById('end_date').value;
    const description = document.getElementById('description').value;
    const payment_amount = document.getElementById('payment_amount').value;

    // API endpoint
    const apiUrl = '/api/care-requests/';  // Replace with your actual endpoint

    try {
        // Send POST request to the API
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`,  // Replace with your auth token logic
            },
            body: JSON.stringify({
                start_date,
                end_date,
                description,
                payment_amount,
                caregiver: null,  // No caregiver assigned yet
            }),
        });

        const result = await response.json();

        // Handle response
        const responseMessage = document.getElementById('responseMessage');
        if (response.ok) {
            responseMessage.textContent = 'Care request submitted successfully!';
            responseMessage.className = 'mt-4 text-green-500 text-center';
            responseMessage.classList.remove('hidden');
        } else {
            responseMessage.textContent = `Error: ${result.error || 'Unable to submit request.'}`;
            responseMessage.className = 'mt-4 text-red-500 text-center';
            responseMessage.classList.remove('hidden');
        }
    } catch (error) {
        console.error('Error:', error);
        const responseMessage = document.getElementById('responseMessage');
        responseMessage.textContent = 'An unexpected error occurred. Please try again.';
        responseMessage.className = 'mt-4 text-red-500 text-center';
        responseMessage.classList.remove('hidden');
    }
});
