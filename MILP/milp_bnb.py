# %%
import matplotlib.pyplot as plt
import numpy as np
from pulp import LpMaximize, LpProblem, LpVariable

# Create the LP problem
problem = LpProblem("BranchAndBound", LpMaximize)

# Define the variables as integers
x1 = LpVariable("x1", lowBound=0, cat="Integer")
x2 = LpVariable("x2", lowBound=0, cat="Integer")

# Define the objective function
problem += 5 * x1 + 6 * x2, "Objective"

# Define the constraints
problem += x1 + x2 <= 50, "Constraint 1"
problem += 4 * x1 + 7 * x2 <= 280, "Constraint 2"

# Solve the problem
problem.solve()

# Print the results
print("Status:", problem.status)
print("x1 =", x1.varValue)
print("x2 =", x2.varValue)
print("Maximized Z =", 5 * x1.varValue + 6 * x2.varValue)

# %%
"""
Plot the feasible region
x_{1}+x_{2}<= 50
4x_{1}+7x_{2}<= 280
x_{1},x_{2}>=0
"""

# Define the inequalities as equations
# x1 + x2 <= 50
# 4x1 + 7x2 <= 280

# Create a range of values for x1
x1 = np.linspace(0, 100, 400)  # Adjust the range as needed

# Calculate x2 for the first inequality
x2_1 = 50 - x1

# Calculate x2 for the second inequality
x2_2 = (280 - 4*x1) / 7

# Plot the lines corresponding to the inequalities
plt.plot(x1, x2_1, label='x1 + x2 <= 50')
plt.plot(x1, x2_2, label='4x1 + 7x2 <= 280')
plt.plot(24, 26, marker='o', fillstyle='none',
         label='Optimal Solution by BnB Method')

# Add dashed lines for the additional equations
plt.plot(x1, 26 * np.ones_like(x1), 'r--', label='x2 ≤ 26')
plt.plot(x1, 27 * np.ones_like(x1), 'g--', label='x2 ≥ 27')
plt.plot(22 * np.ones_like(x1), x1, 'b--', label='x1 ≤ 22')
plt.plot(23 * np.ones_like(x1), x1, 'm--', label='x1 ≥ 23')

# Fill the feasible region
plt.fill_between(x1, 0, np.minimum(x2_1, x2_2), where=(x2_1 >= 0) & (
    x2_2 >= 0), color='gray', alpha=0.5, label='Feasible Region')

# Add labels and legend
plt.xlabel('x1')
plt.ylabel('x2')
plt.xlim(0, 55)
plt.ylim(0, 55)
plt.legend()
plt.grid(True)

# Show the plot
plt.show()
