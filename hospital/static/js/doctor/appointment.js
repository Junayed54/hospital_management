// document.getElementById('appointmentForm').addEventListener('submit', async function(e) {
//   e.preventDefault();  // Prevent form submission
//   const formData = new FormData(this);

//   // Get doctor ID from the URL
//   const doctorId = window.location.pathname.split('/').filter(Boolean).pop();  // Extracts doctor ID from the URL

//   // Add doctor ID to the data
//   formData.append('doctor', doctorId);

//   // Convert formData to JSON
//   const data = Object.fromEntries(formData.entries());

//   try {
//       const response = await fetch('/api/appointments/', {
//           method: 'POST',
//           headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
//           body: JSON.stringify(data)
//       });

//       if (response.ok) {
//           alert('Appointment successfully booked!');
//           // window.location.reload();  // Optionally reload or redirect
//       } else {
//           const result = await response.json();
//           alert('Error: ' + JSON.stringify(result));
//       }
//   } catch (error) {
//       console.error('Error:', error);
//       alert('An error occurred while booking the appointment.');
//   }
// });

// // Function to get CSRF token from cookie
// function getCSRFToken() {
//   const cookies = document.cookie.split('; ');
//   for (const cookie of cookies) {
//       const [name, value] = cookie.split('=');
//       if (name === 'csrftoken') return value;
//   }
//   return '';
// }


document.getElementById('appointmentForm').addEventListener('submit', async function (e) {
    e.preventDefault(); // Prevent default form submission
    const formData = new FormData(this);

    // Extract doctor ID and availability ID from the URL
    const pathParts = window.location.pathname.split('/').filter(Boolean); // Split URL path and remove empty parts
    const doctorId = pathParts[pathParts.length - 2]; // Second last part is the doctor ID
    const availabilityId = pathParts[pathParts.length - 1]; // Last part is the availability ID

    // Add doctor and availability IDs to the form data
    formData.append('doctor', doctorId);
    formData.append('availability', availabilityId);

    // Convert formData to JSON
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch('/api/appointments/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            alert('Appointment successfully booked!');
            // Optionally redirect or reload the page
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
