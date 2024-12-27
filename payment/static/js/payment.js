document.addEventListener("DOMContentLoaded", () => {
    const paymentsList = document.getElementById("payments-container");
    const addPaymentForm = document.getElementById("add-payment-form");
    const paymentMethodSelect = document.getElementById("payment-method-select");
  
    // Fetch Payments
    const fetchPayments = async () => {
      try {
        const response = await fetch("/payments/");
        if (!response.ok) throw new Error("Failed to fetch payments");
  
        const data = await response.json();
        paymentsList.innerHTML = "";
  
        data.forEach((payment) => {
          const li = document.createElement("li");
          li.textContent = `Method: ${payment.method.title}, Amount: ${payment.amount}, Description: ${payment.description}`;
          paymentsList.appendChild(li);
        });
      } catch (error) {
        console.error(error);
      }
    };
  
    // Fetch Payment Methods for Dropdown
    const fetchPaymentMethods = async () => {
      try {
        const response = await fetch("/payment-methods/");
        if (!response.ok) throw new Error("Failed to fetch payment methods");
  
        const methods = await response.json();
        paymentMethodSelect.innerHTML = "";
  
        methods.forEach((method) => {
          const option = document.createElement("option");
          option.value = method.id;
          option.textContent = method.title;
          paymentMethodSelect.appendChild(option);
        });
      } catch (error) {
        console.error(error);
      }
    };
  
    // Add Payment
    addPaymentForm.addEventListener("submit", async (e) => {
      e.preventDefault();
  
      const method = paymentMethodSelect.value;
      const amount = document.getElementById("payment-amount").value;
      const description = document.getElementById("payment-description").value;
  
      try {
        const response = await fetch("/payments/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ method, amount, description }),
        });
        if (!response.ok) throw new Error("Failed to make payment");
  
        fetchPayments(); // Refresh list
        addPaymentForm.reset(); // Clear form
      } catch (error) {
        console.error(error);
      }
    });
  
    fetchPayments(); // Initial load
    fetchPaymentMethods(); // Load payment methods for form
  });
  