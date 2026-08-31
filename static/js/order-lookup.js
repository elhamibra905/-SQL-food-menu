const orderLookupForm = document.getElementById("orderLookupForm");
const orderIdInput = document.getElementById("orderId");
const errorMessage = document.getElementById("errorMessage");
const orderResult = document.getElementById("orderResult");

orderLookupForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const orderId = orderIdInput.value;

  errorMessage.textContent = "";
  orderResult.innerHTML = "";

  try {
    const response = await fetch(`/api/orders/${orderId}`);

    const data = await response.json();

    if (!response.ok) {
      errorMessage.textContent = data.error || "Order not found.";
      return;
    }

    orderResult.innerHTML = `
            <div class="order-card">

                <h2>Order #${data.id}</h2>

                <p>
                    <strong>Customer:</strong>
                    ${data.customer}
                </p>

                <p>
                    <strong>Items:</strong>
                    ${data.items}
                </p>

                <p>
                    <strong>Quantity:</strong>
                    ${data.quantity}
                </p>

                <p>
                    <strong>Total:</strong>
                    ETB ${Number(data.total_price).toFixed(2)}
                </p>

                <div class="order-status">
                    <strong>Status:</strong>

                    <span class="status-badge status-${data.status}">
                        ${data.status}
                    </span>
                </div>

            </div>
        `;
  } catch (error) {
    console.error("Order lookup error:", error);

    errorMessage.textContent = "Something went wrong. Please try again.";
  }
});
