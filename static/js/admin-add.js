const form = document.getElementById("addOrderForm");
const errorMessage = document.getElementById("errorMessage");

const token = localStorage.getItem("adminToken");

// Check if admin is logged in
if (!token) {
  window.location.href = "/admin/login";
} else {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const customer = document.getElementById("customer").value.trim();
    const items = document.getElementById("items").value.trim();
    const quantity = document.getElementById("quantity").value;
    const total_price = document.getElementById("total_price").value;

    try {
      const response = await fetch("/api/admin/orders", {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },

        body: JSON.stringify({
          customer,
          items,
          quantity,
          total_price,
        }),
      });

      // Token is missing, invalid, or expired
      if (response.status === 401 || response.status === 403) {
        localStorage.removeItem("adminToken");
        window.location.href = "/admin/login";
        return;
      }

      const data = await response.json();

      // Other errors
      if (!response.ok) {
        errorMessage.textContent = data.error || "Failed to create order";
        return;
      }

      // Success
      alert("Order created successfully!");

      // Go back to dashboard
      window.location.href = "/admin/dashboard";
    } catch (error) {
      console.error("Add order error:", error);

      errorMessage.textContent =
        "Something went wrong while creating the order.";
    }
  });
}
