document.getElementById("departmentForm").addEventListener("submit", async function (event) {
    event.preventDefault(); // Prevent form submission from reloading the page
    
    // Collect form data
    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());

    // Validate required fields (if necessary)
    if (!data.name) {
        alert("Please provide a department name.");
        return;
    }

    // Get the JWT token from localStorage or sessionStorage
    const token = localStorage.getItem("access_token");  // Assuming the token is stored in localStorage

    if (!token) {
        alert("Authentication required.");
        return;
    }

    // Send data to the API with the JWT token in the Authorization header
    try {
        const response = await fetch('/api/create-department/', {  // Replace with your API endpoint
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`  // Include the token in the header
            },
            body: JSON.stringify(data),
        });

        if (response.ok) {
            const result = await response.json();
            const responseMessage = document.getElementById("responseMessage");
            responseMessage.classList.remove("hidden");
            responseMessage.innerText = "Department created successfully!";
            responseMessage.classList.remove("bg-red-100", "text-red-700");
            responseMessage.classList.add("bg-green-100", "text-green-700");
            this.reset(); // Clear the form
        } else {
            console.log(response);
            const errorData = await response.json();
            alert("Error: " + JSON.stringify(errorData.detail));
        }
    } catch (error) {
        alert("An unexpected error occurred. Please try again.");
        console.error(error);
    }
});
