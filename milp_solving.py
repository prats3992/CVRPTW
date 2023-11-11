"""
Maximize z=x1+10x2
Subject to
.2x1+4>=x2
-.2x1+6>=x2
10x1+1>=x2
x1,x2>=0
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog
import matplotlib.pyplot as plt

# Define the coefficients of the objective function
c = [-1, -10]

# Define the coefficients of the constraints
A = [[0.2, -1], [-0.2, -1], [-10, -1]]
b = [-4, -6, -1]

# Define the bounds of the decision variables
x0_bounds = (-10, 20)
x1_bounds = (-10, 20)

# Solve the linear programming problem
res = linprog(c, A_ub=A, b_ub=b, bounds=[x0_bounds, x1_bounds])

# Print the solution
print(res)

# Plot the feasible region and the optimal solution
x0 = np.linspace(0, 20, 100)
x1_1 = 0.2*x0 + 4
x1_2 = -0.2*x0 + 6
x1_3 = 10*x0 + 1
plt.plot(x0, x1_1, label='0.2x1 - x2 + 4 <= 0')
plt.plot(x0, x1_2, label='-0.2x1 - x2 + 6 <= 0')
plt.plot(x0, x1_3, label='10x1 - x2 + 1 <= 0')
plt.fill_between(x0, 0, x1_1, where=(x1_1 <= x1_2) &
                 (x1_1 <= x1_3), color='grey', alpha=0.5)
plt.fill_between(x0, 0, x1_2, where=(x1_2 <= x1_1) &
                 (x1_2 <= x1_3), color='grey', alpha=0.5)
plt.fill_between(x0, 0, x1_3, where=(x1_3 <= x1_1) &
                 (x1_3 <= x1_2), color='grey', alpha=0.5)
plt.xlim(0, 22)
plt.ylim(0, 22)
plt.xlabel('x1')
plt.ylabel('x2')
plt.plot(res.x[0], res.x[1], 'o', label="Upper Bound")
plt.plot(0, 0, 'mo', label="Lower Bound", zorder=10)
plt.legend()
plt.show()
