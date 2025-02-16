document.getElementById('receiptInput').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    fetch('/scan-receipt', {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log("Scanned Purchases:", data.purchases);
        updateBudget(data.purchases);  // Call a function to update the UI with the scanned purchases
    })
    .catch(error => console.error("Error scanning receipt:", error));
});

function updateFlippingNumber(newNumber) {
    const flipNumber = document.getElementById("flip-number");

    if (!flipNumber) return; // Ensure the element exists

    // Create a new span for the flip animation
    const newSpan = document.createElement("span");
    newSpan.className = "block absolute inset-0 transition-transform duration-500 ease-in-out";
    newSpan.textContent = newNumber;

    // Add animation effect
    newSpan.style.transform = "rotateX(90deg)";
    newSpan.style.opacity = "0";

    // Append the new number to the container
    flipNumber.appendChild(newSpan);

    // Animate old number out and new number in
    setTimeout(() => {
        if (flipNumber.firstElementChild) {
            flipNumber.firstElementChild.style.transform = "rotateX(-90deg)";
            flipNumber.firstElementChild.style.opacity = "0";
        }
        newSpan.style.transform = "rotateX(0deg)";
        newSpan.style.opacity = "1";
    }, 50);

    // Remove old number after animation
    setTimeout(() => {
        if (flipNumber.firstElementChild) {
            flipNumber.firstElementChild.remove();
        }
    }, 500);
}

// Example: Update the number every 3 seconds for testing
let currentNumber = 100;
setInterval(() => {
    currentNumber -= 5; // Decrease for demonstration
    updateFlippingNumber(currentNumber);
}, 3000);

function updateBudget(purchases) {
    let totalSpent = purchases.reduce((sum, item) => sum + item.amount, 0);
    
    fetch('/submit-purchases', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ purchases })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Updated Budget:", data.remainingBudget);
        updateFlippingNumber(data.remainingBudget);

        // After updating the budget, display category totals
        displayCategoryTotals(purchases);
    })
    .catch(error => console.error("Error updating budget:", error));
}

function displayCategoryTotals(purchases) {
    const categoryTotals = calculateCategoryTotals(purchases);
    const categoryTotalsContainer = document.getElementById('category-totals');
    
    // Clear previous content
    categoryTotalsContainer.innerHTML = '';

    // Create and append elements for each category
    Object.entries(categoryTotals).forEach(([category, total]) => {
        const listItem = document.createElement('li');
        listItem.className = 'text-lg mt-2'; // Add Tailwind classes for styling
        listItem.textContent = `${category}: $${total.toFixed(2)}`;
        categoryTotalsContainer.appendChild(listItem);
    });
}
function calculateCategoryTotals(purchases) {
    return purchases.reduce((totals, purchase) => {
        totals[purchase.category] = (totals[purchase.category] || 0) + purchase.amount;
        return totals;
    }, {});
}

function calculateCategoryTotals(items) {
    let categoryTotals = {};

    // Sum totals for each category
    items.forEach(item => {
        if (categoryTotals[item.category]) {
            categoryTotals[item.category] += item.amount;

            async function handleReceiptUpload(event) {
                const file = event.target.files[0];
                if (!file) return;
            
                try {
                    const formData = new FormData();
                    formData.append("file", file);
                    const response = await fetch('/scan-receipt', {
                        method: "POST",
                        body: formData
                    });
                    const data = await response.json();
                    console.log("Scanned Purchases:", data.purchases);
                    await updateBudget(data.purchases);
                    displayCategoryTotals(data.purchases); // Add this line
                } catch (error) {
                    console.error("Error scanning receipt:", error);
                    // Show user-friendly error message
                }
            }
            
            document.addEventListener('DOMContentLoaded', () => {
                // Other initialization code...
            
                // If you have initial data, display it
                const initialPurchases = []; // Replace with actual initial data if available
                displayCategoryTotals(initialPurchases);
            });
            