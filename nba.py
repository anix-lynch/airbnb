#!/usr/bin/env python3

import nbformat as nbf

# Read the Python script
with open('airbnb.py', 'r') as file:
	script = file.read()
	
# Create a new notebook
nb = nbf.v4.new_notebook()

# Split the script into code cells based on empty lines
code_cells = script.split('\n\n')

# Create notebook cells
cells = [nbf.v4.new_code_cell(cell) for cell in code_cells]

# Add the cells to the notebook
nb['cells'] = cells

# Write the notebook to a file
with open('Airbnb_Data_Analysis.ipynb', 'w') as f:
	nbf.write(nb, f)
	
print("Jupyter Notebook has been created successfully.")
