
//when a change occurs
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
        displayCategoryTotals(data.purchases); 
    })
    .catch(error => console.error("Error scanning receipt:", error));
});

//setting up flipping number shell for budget input
function updateFlippingNumber(newNumber) {
    const flipNumber = document.getElementById("flip-number");

    if (!flipNumber) return;

    const newSpan = document.createElement("span");
    newSpan.id = "currBudget";
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

// Updates the category totals list with the new totals.
function displayCategoryTotals(purchases) {
    const categoryTotals = calculateCategoryTotals(purchases);
    const categoryTotalsContainer = document.getElementById('category-totals');
    
    categoryTotalsContainer.innerHTML = '';

    // Loops through each category and adds a list item for it
    Object.entries(categoryTotals).forEach(([category, total]) => {
        const listItem = document.createElement('li');
        // Set the class to add text color
        listItem.className = 'text-lg mt-2 text-[#1e1d1d]';
        // Set the text content to the category and total
        listItem.textContent = `${category}: $${total.toFixed(2)}`;
        // Add the list item to the container
        categoryTotalsContainer.appendChild(listItem);
    });
}


 //Calculates the total amount spent in each category from an array of purchases.

function calculateCategoryTotals(purchases) {
    // Creating an object to store the total amount spent in each category
    const totals = {};

    // Loop through each purchase and add the price to the total
    purchases.forEach(purchase => {
        // If the category is not already in the totals object, add it
        if (!totals[purchase.category]) {
            totals[purchase.category] = 0;
        }
        // Adding price to the total
        totals[purchase.category] += purchase.price;
    });

    return totals;
}


document.addEventListener('DOMContentLoaded', () => {
    const initialPurchases = []; 
    displayCategoryTotals(initialPurchases);
});

//function to handle budget input
function updateBudget(scanned_purchases) {
    const container = document.querySelector('#currBudget');
    var budget = container.textConter;
    const userId = 1; // Replace with actual user ID after login implementation
    const totalSpent = calculateCategoryTotals(scanned_purchases);
    const totalAmountSpent = Object.values(totalSpent).reduce((a, b) => a + b, 0);

    console.log("UPDATE");

    try {
        fetch('/update-budget', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_id: userId, purchases: scanned_purchases, budget: budget })
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error(`Error updating budget: ${response.status}`);
            }
        })
        .then(data => {
            if (data.message) {
                console.log("B");
                updateFlippingNumber(data.new_budget);
            } else {
                console.error('Error updating budget:', data.error);
            }
        })
        .catch(error => console.error('Error:', error));
    } catch (error) {
        console.error('Error:', error);
    }
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


// Updates the pie chart with the monthly averages of each category
//waiting for database setup
function updatePieChart(monthlyAverages) {
    const ctx = document.querySelector('.aspect-square').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'pie',

        // The data for dataset
        data: {
            labels: Object.keys(monthlyAverages),

            datasets: [{
                data: Object.values(monthlyAverages),

                // The background color of the bars
                backgroundColor: [
                    'pink', '#EA638C', '#89023E', '#30343F', '#FAFAFF'
                ]
            }]
        },

        // Configuration options go here
        options: {
            // Making the chart responsive
            responsive: true,

            // The title of the chart
            title: {
                display: true,
                text: 'Monthly Average Expenses by Category'
            }
        }
    });
}




// Get the pie chart element
const pieChart = document.querySelector('.pie-chart-overlay').parentElement;

// Set the animation duration and easing
const animationDuration = 500; // 0.5 seconds
const animationEasing = 'ease-out';

// Set the percentage data, dummy code for now
const percentages = [50, 20, 30];

// Calculate the total percentage
const totalPercentage = percentages.reduce((a, b) => a + b, 0);

// Animate the pie chart
function animatePieChart() {
  let currentAngle = 0;
  const intervalTime = animationDuration / 360; // calculate interval time based on animationDuration
  const intervalId = setInterval(() => {
    const angle1 = (percentages[0] / totalPercentage) * currentAngle;
    const angle2 = (percentages[1] / totalPercentage) * currentAngle;
    const angle3 = (percentages[2] / totalPercentage) * currentAngle;

    pieChart.style.backgroundImage = `conic-gradient(pink 0deg ${angle1}deg, #EA638C ${angle1}deg ${angle1 + angle2}deg, #89023E ${angle1 + angle2}deg ${currentAngle}deg)`;

    currentAngle += 1;
    if (currentAngle >= 360) {
      clearInterval(intervalId);
    }
  }, intervalTime); // use the calculated interval time
}
// Execute the animation on page load
window.addEventListener('load', animatePieChart);

document.addEventListener('DOMContentLoaded', function() {
    const user_id = 1;
    fetch('/get_budget', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({user_id: user_id}),
    })
    .then(response => response.json())
    .then(data => {
        const currBudgetDisplay = document.getElementById('currBudget');
        currBudgetDisplay.textContent = `${data.curr_budget}`;
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const openModalBtns = document.querySelectorAll('.openModalBtn');
    const closeModalBtns = document.querySelectorAll('.closeModalBtn');
    const modals = document.querySelectorAll('.modal');

    openModalBtns.forEach((btn, index) => {
        btn.addEventListener('click', () => {
            console.log("Opening modal", index);
            modals[index].classList.remove('hidden');
        });
    });

    closeModalBtns.forEach((btn, index) => {
        btn.addEventListener('click', () => {
            console.log("Closing modal", index);
            modals[index].classList.add('hidden');
        });
    });

    // Close modal when clicking outside
    window.addEventListener('click', (event) => {
        modals.forEach((modal) => {
            if (event.target === modal) {
                modal.classList.add('hidden');
            }
        });
    });
});

// Submit Budget through Settings
document.addEventListener('DOMContentLoaded', function() {
    const submitBudgetBtn = document.getElementById('submit-budget');
    const budgetInput = document.getElementById('budgetInput');
    const currBudgetDisplay = document.getElementById('currBudget');

    submitBudgetBtn.addEventListener('click', function() {
        const budgetValue = budgetInput.value;
        if (budgetValue) {
            fetch('/update-budget', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({budget: budgetValue}),
            })
            .then(response => response.json())
            .then(data => {
                currBudgetDisplay.textContent = `$${data.new_budget}`;
            })
            .catch((error) => {
                console.error('Error:', error);
                alert('An error occurred. Please try again.');
            });
        } else {
            alert('Please enter a valid budget amount.');
        }
    });
});
