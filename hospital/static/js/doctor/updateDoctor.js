document.getElementById("updateDoctorForm").addEventListener("submit", async function (e) {
    e.preventDefault(); // Prevent default form submission

    const formData = {
        full_name: document.getElementById("full_name").value,
        specialty: document.getElementById("specialty").value,
        bio: document.getElementById("bio").value,
        experience_years: document.getElementById("experience_years").value,
        education: document.getElementById("education").value,
        consultation_fee: document.getElementById("consultation_fee").value,
        contact_email: document.getElementById("contact_email").value,
        contact_phone: document.getElementById("contact_phone").value,
    };

    const responseMessage = document.getElementById("responseMessage");
    responseMessage.classList.add("hidden"); // Hide the message initially

    try {
        const response = await fetch("/doctor/update/", {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${localStorage.getItem("access_token")}` // Replace with your token logic
            },
            body: JSON.stringify(formData),
        });

        if (response.ok) {
            const data = await response.json();
            responseMessage.textContent = "Profile updated successfully!";
            responseMessage.classList.remove("hidden");
            responseMessage.classList.add("text-green-500");
        } else {
            const error = await response.json();
            responseMessage.textContent = `Error: ${error.detail || "Failed to update profile"}`;
            responseMessage.classList.remove("hidden");
            responseMessage.classList.add("text-red-500");
        }
    } catch (error) {
        console.error("Error:", error);
        responseMessage.textContent = "An unexpected error occurred.";
        responseMessage.classList.remove("hidden");
        responseMessage.classList.add("text-red-500");
    }
});
