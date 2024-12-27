document.addEventListener("DOMContentLoaded", () => {
    const paymentMethodsList = document.getElementById("payment-methods-container");
    const addMethodForm = document.getElementById("add-payment-method-form");
  
    // Fetch Payment Methods
    const fetchPaymentMethods = async () => {
      try {
        const response = await fetch("/payment-methods/");
        if (!response.ok) throw new Error("Failed to fetch payment methods");
  
        const data = await response.json();
        paymentMethodsList.innerHTML = "";
  
        data.forEach((method) => {
          const li = document.createElement("li");
          li.textContent = `${method.title} - ${method.description}`;
          paymentMethodsList.appendChild(li);
        });
      } catch (error) {
        console.error(error);
      }
    };
  
    // Add Payment Method
    addMethodForm.addEventListener("submit", async (e) => {
      e.preventDefault();
  
      const title = document.getElementById("method-title").value;
      const description = document.getElementById("method-description").value;
  
      try {
        const response = await fetch("/payment-methods/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ title, description }),
        });
        if (!response.ok) throw new Error("Failed to add payment method");
  
        fetchPaymentMethods(); // Refresh list
        addMethodForm.reset(); // Clear form
      } catch (error) {
        console.error(error);
      }
    });
  
    fetchPaymentMethods(); // Initial load
  });
  