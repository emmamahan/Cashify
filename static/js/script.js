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
        updateBudget(data.purchases);
        displayCategoryTotals(data.purchases);  // Add this line
    })
    .catch(error => console.error("Error scanning receipt:", error));
});

function updateFlippingNumber(newNumber) {
    const flipNumber = document.getElementById("flip-number");

    if (!flipNumber) return;

    const newSpan = document.createElement("span");
    newSpan.className = "block absolute inset-0 transition-transform duration-500 ease-in-out";
    newSpan.textContent = newNumber;

    newSpan.style.transform = "rotateX(90deg)";
    newSpan.style.opacity = "0";

    flipNumber.appendChild(newSpan);

    setTimeout(() => {
        if (flipNumber.firstElementChild) {
            flipNumber.firstElementChild.style.transform = "rotateX(-90deg)";
            flipNumber.firstElementChild.style.opacity = "0";
        }
        newSpan.style.transform = "rotateX(0deg)";
        newSpan.style.opacity = "1";
    }, 50);

    setTimeout(() => {
        if (flipNumber.firstElementChild) {
            flipNumber.firstElementChild.remove();
        }
    }, 500);
}


function displayCategoryTotals(purchases) {
    const categoryTotals = calculateCategoryTotals(purchases);
    const categoryTotalsContainer = document.getElementById('category-totals');
    
    categoryTotalsContainer.innerHTML = '';

    Object.entries(categoryTotals).forEach(([category, total]) => {
        const listItem = document.createElement('li');
        listItem.className = 'text-lg mt-2 text-[#1e1d1d]';  // Add text color
        listItem.textContent = `${category}: $${total.toFixed(2)}`;
        categoryTotalsContainer.appendChild(listItem);
    });
}

function calculateCategoryTotals(purchases) {
    return purchases.reduce((totals, purchase) => {
        totals[purchase.category] = (totals[purchase.category] || 0) + purchase.price;
        return totals;
    }, {});
}

// Remove the setInterval for updating the flipping number

document.addEventListener('DOMContentLoaded', () => {
    // If you have initial data, display it
    const initialPurchases = []; // Replace with actual initial data if available
    displayCategoryTotals(initialPurchases);
});

// Add this function to handle budget input
function updateBudget(scanned_purchases) {
    const budget = document.getElementById('budgetInput').value;
    const userId = 1; // Replace with actual user ID
    const totalSpent = calculateCategoryTotals(scanned_purchases);
    const totalAmountSpent = Object.values(totalSpent).reduce((a, b) => a + b, 0);

    const newBudget = parseFloat(budget) - totalAmountSpent

    fetch('/update-budget', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId, purchases: scanned_purchases, budget: newBudget })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            console.log("B");
            updateFlippingNumber(data.new_budget);
            
        } else {
            console.error('Error updating budget:', data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}

// Modify the submitPurchases function
function submitPurchases(purchases) {
    const userId = 1; // Replace with actual user ID

    fetch('/submit-purchases', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ purchases: purchases, user_id: userId })
    })
    .then(response => response.json())
    .then(data => {
        updateFlippingNumber(data.remainingBudget);
        updatePieChart(data.categoryDistribution);
    })
    .catch(error => console.error('Error:', error));
}

function updatePieChart(monthlyAverages) {
    const ctx = document.querySelector('.aspect-square').getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: Object.keys(monthlyAverages),
            datasets: [{
                data: Object.values(monthlyAverages),
                backgroundColor: [
                    'pink', '#EA638C', '#89023E', '#30343F', '#FAFAFF'
                ]
            }]
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Monthly Average Expenses by Category'
            }
        }
    });
}
