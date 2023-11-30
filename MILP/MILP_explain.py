# %%
import matplotlib.pyplot as plt
import numpy as np

# %% LP
# Define the lines
x = np.arange(-2, 11)
y1 = 10 - x
y2 = x - 5
y3 = np.zeros_like(x)

# Plot the lines
plt.plot(x, y1, label='x + y = 10', marker='o')
plt.plot(x, y2, label='x - y = 5', marker='^', color='r')

# Set the x and y limits
plt.xlim(-2, 10)
plt.ylim(-2, 10)

# Set the x and y labels
plt.xlabel('x')
plt.ylabel('y')

# Add a legend
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

# Show the plot
plt.show()

# %% MILP
# Define the lines
x = np.arange(-2, 11)
y1 = 10 - x
y2 = x - 5
y3 = np.zeros_like(x)

# Plot the lines
plt.plot(x, y1, label='x + y = 10', marker='o')
plt.plot(x, y2, label='x - y = 5', marker='^', color='r')
# plt.fill_between(x, y1, y2, where=y1 > y2, color='grey', alpha=0.5)
# plt.fill_between(x, y1, y2, where=y1 < y2, color='grey', alpha=0.5)
for i in range(len(x)):
    plt.plot(y3+i, x, '--', label=f'x = {i}')

# Set the x and y limits
plt.xlim(-2, 10)
plt.ylim(-2, 10)

# Set the x and y labels
plt.xlabel('x')
plt.ylabel('y')

# Add a legend
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

# Show the plot
plt.show()
