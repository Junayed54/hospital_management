document.getElementById("doctorForm").addEventListener("submit", async function (event) {
    event.preventDefault(); // Prevent form submission from reloading the page

    // Collect form data, including files
    const formData = new FormData(this);

    // Validate required fields (if necessary)
    const data = Object.fromEntries(formData.entries());
    if (!data.department || !data.position) {
        alert("Please select both department and position.");
        return;
    }

    // Send data to the API
    try {
        const response = await fetch('/api/create-doctor/', { // Replace with your API endpoint
            method: 'POST',
            body: formData, // Use formData directly for multipart/form-data
        });

        if (response.ok) {
            const result = await response.json();
            const responseMessage = document.getElementById("responseMessage");
            responseMessage.classList.remove("hidden");
            responseMessage.innerText = "Doctor created successfully!";
            responseMessage.classList.remove("bg-red-100", "text-red-700");
            responseMessage.classList.add("bg-green-100", "text-green-700");
            this.reset(); // Clear the form
        } else {
            const errorData = await response.json();
            alert("Error: " + JSON.stringify(errorData));
        }
    } catch (error) {
        alert("An unexpected error occurred. Please try again.");
        console.error(error);
    }
});
