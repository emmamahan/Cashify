import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Backend: Expense data and calculations
class BudgetPlanner:
    def __init__(self, budget):
        self.budget = budget
        self.expenses = {}

    def add_expense(self, category, amount):
        if category in self.expenses:
            self.expenses[category] += amount
        else:
            self.expenses[category] = amount
    def calculate_remaining_budget(self):
        total_spent = sum(self.expenses.values())
        return self.budget - total_spent

    def get_expense_distribution(self):
        return self.expenses

# GUI Application
class BudgetPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Budget Planner")
        self.root.geometry("600x600")
        self.root.config(bg="#f5f5f5")

        self.budget_planner = None

        # GUI elements
        self.create_widgets()

    def create_widgets(self):
        # Header
        header = tk.Label(self.root, text="Budget Planner", font=("Arial", 20, "bold"), fg="#4CAF50", bg="#f5f5f5")
        header.pack(pady=10)

        # Budget Input
        budget_label = tk.Label(self.root, text="Enter Monthly Budget ($):", font=("Arial", 14), bg="#f5f5f5")
        budget_label.pack(pady=5)
        self.budget_entry = tk.Entry(self.root, font=("Arial", 14))
        self.budget_entry.pack(pady=5)
        set_budget_button = tk.Button(self.root, text="Set Budget", font=("Arial", 12), bg="#4CAF50", fg="white", command=self.set_budget)
        set_budget_button.pack(pady=10)

        # Expense Inputs
        expense_frame = tk.Frame(self.root, bg="#f5f5f5")
        expense_frame.pack(pady=20)

        category_label = tk.Label(expense_frame, text="Category:", font=("Arial", 12), bg="#f5f5f5")
        category_label.grid(row=0, column=0, padx=5)
        self.category_entry = ttk.Combobox(expense_frame, values=["Food", "Rent", "Utilities", "Transport", "Miscellaneous"], font=("Arial", 12))
        self.category_entry.grid(row=0, column=1, padx=5)

        amount_label = tk.Label(expense_frame, text="Amount ($):", font=("Arial", 12), bg="#f5f5f5")
        amount_label.grid(row=0, column=2, padx=5)
        self.amount_entry = tk.Entry(expense_frame, font=("Arial", 12))
        self.amount_entry.grid(row=0, column=3, padx=5)

        add_expense_button = tk.Button(expense_frame, text="Add Expense", font=("Arial", 12), bg="#4CAF50", fg="white", command=self.add_expense)
        add_expense_button.grid(row=0, column=4, padx=5)

        # Remaining Budget
        self.remaining_budget_label = tk.Label(self.root, text="Remaining Budget: $0.00", font=("Arial", 16), bg="#f5f5f5", fg="#FF5722")
        self.remaining_budget_label.pack(pady=10)

        # Expense Visualization
        self.canvas_frame = tk.Frame(self.root, bg="#f5f5f5")
        self.canvas_frame.pack(fill="both", expand=True)

    def set_budget(self):
        try:
            budget = float(self.budget_entry.get())
            self.budget_planner = BudgetPlanner(budget)
            self.update_remaining_budget()
            messagebox.showinfo("Success", "Monthly budget set successfully!")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid budget amount.")

    def add_expense(self):
        if not self.budget_planner:
            messagebox.showerror("Error", "Please set a budget first.")
            return

        try:
            category = self.category_entry.get()
            amount = float(self.amount_entry.get())

            if not category:
                messagebox.showerror("Error", "Please select a category.")
                return

            self.budget_planner.add_expense(category, amount)
            self.update_remaining_budget()
            self.update_pie_chart()
            self.category_entry.set("")
            self.amount_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount.")

    def update_remaining_budget(self):
        remaining = self.budget_planner.calculate_remaining_budget()
        self.remaining_budget_label.config(text=f"Remaining Budget: ${remaining:.2f}")

    def update_pie_chart(self):
        expenses = self.budget_planner.get_expense_distribution()
        categories = list(expenses.keys())
        amounts = list(expenses.values())

        # Clear previous chart
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        # Create pie chart
        figure = Figure(figsize=(5, 4), dpi=100)
        ax = figure.add_subplot(111)
        ax.pie(amounts, labels=categories, autopct="%1.1f%%", startangle=90, colors=["#FF9999", "#FFCC99", "#FFFF99", "#99FF99", "#99CCFF"])
        ax.set_title("Expense Distribution")

        canvas = FigureCanvasTkAgg(figure, self.canvas_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetPlannerApp(root)
    root.mainloop()
