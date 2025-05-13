import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import re # Regular Expressions

def tokenize_equation(equation_text):
    # Remove extra whitespace
    equation_text = equation_text.strip()
    
    # List to store tokens
    tokens = []
    
    # Define patterns using regex
    patterns = [
        (r'[a-zA-Z][a-zA-Z0-9]*', 'identifier'),  # Variables (e.g., x, y)
        (r'\d+\.\d+|\d+', 'number'),              # Integers (e.g., 10) or decimals (e.g., 10.5)
        (r'[+\-*/=]', 'operator'),                # Operators (+, -, *, /, =)
        (r'[()]', 'parenthesis'),                 # Parentheses ( ( , ) )
        (r'[;]', 'semicolon'),                    # Semicolon ( ; ) 
    ]
    
    index = 0 # To give an order to each token (e.g., 0, 1, 2, ...)
    pos = 0 # Current position in the string
    
    while pos < len(equation_text):
        matched = False # Flag to check if a pattern matched
        for pattern, token_type in patterns:
            regex = re.compile(pattern) # Compile the regex pattern
            match = regex.match(equation_text, pos) # Match the pattern at the current position
            if match:
                token = match.group(0) # Get the matched token
                tokens.append((token, token_type, index)) # Adds a tuple to the tokens list.
                pos += len(token)
                index += 1
                matched = True
                break
        if not matched:
            # Show error message for unsupported character
            messagebox.showerror("Error", f"Unsupported character: {equation_text[pos]} at position {pos}")
            pos += 1
    
    return tokens

# Lexical Analyzer 
def scan_equation():
    # Get the equation from the input field
    equation_text = entry.get()
    
    # Clear the old tables and text
    for row in token_table.get_children():
        token_table.delete(row)
    for row in transition_table.get_children():
        transition_table.delete(row)
    parse_text.delete(1.0, tk.END)
    result_label.config(text="")
    
    # Check if the equation is empty
    if not equation_text:
        messagebox.showwarning("Warning", "Please enter the code!")
        return
    
    # Tokenize the equation
    tokens = tokenize_equation(equation_text)
    
    # Add results to the table with alternating colors
    for i, (token, token_type, index) in enumerate(tokens):
        # Use 'odd' tag for odd-numbered rows and 'even' tag for even-numbered rows
        tag = 'odd' if i % 2 == 0 else 'even'
        token_table.insert('', 'end', values=(token, token_type, index), tags=(tag,))
        
    # Parse the tokens using the transition table
    is_accepted, final_state, transition_path = parse_equation(tokens)
    
    # Populate the transition table with the dynamic transition path
    for i, transition in enumerate(transition_path):
        tag = 'odd' if i % 2 == 0 else 'even'
        transition_table.insert('', 'end', values=(
            transition['current_state'],
            transition['input_type'],
            transition['next_state'],
            transition['final']
        ), tags=(tag,))
    
    # Parse the tokens using the predictive parser
    _, parse_trace = parse_with_trace(tokens)
    
    # Display the parsing trace as text
    parse_text.insert(tk.END, "Predictive Parser\n")
    for line in parse_trace:
        parse_text.insert(tk.END, line + "\n")
    if is_accepted:
        parse_text.insert(tk.END, "Parsing completed successfully!")
    else:
        parse_text.insert(tk.END, "Syntax error!")

# Syntax Analysis
def parse_equation(tokens):
    # Define states
    states = {
        'q0': {'final': "Yes"},
        'q1': {'final': "Yes"},
        'q3': {'final': "Yes"},
        'qErr': {'final': "No"}
    }
    
    # Define transition table
    transitions = {
        'q0': {'letter': 'q1'},
        'q1': {'=': 'q3'},
        'q3': {'letter': 'q3', 'other': 'qErr'},
        'qErr': {'letter': 'qErr', 'other': 'qErr'}
    }
    
    # Current state starts at q0
    current_state = 'q0'
    pos = 0
    transition_path = []  # To store the transition path
    
    while pos < len(tokens):
        token, token_type, _ = tokens[pos]
        
        # Map token types to input types for the transition table
        if token_type == 'identifier':
            input_type = 'letter'
        elif token_type == 'operator' and token == '=':
            input_type = '='
        else:
            input_type = 'other'
        
        # Record the current transition
        transition_path.append({
            'current_state': current_state,
            'input_type': input_type,
            'next_state': transitions[current_state][input_type] if current_state in transitions and input_type in transitions[current_state] else 'qErr',
            'final': states[transitions[current_state][input_type]]['final'] if current_state in transitions and input_type in transitions[current_state] else 'No'
        })
        
        # Check if there's a transition for the current state and input type
        if current_state in transitions and input_type in transitions[current_state]:
            current_state = transitions[current_state][input_type]
        else:
            current_state = 'qErr'
        
        pos += 1
    
    # Check if the final state is accepting
    is_accepted = states[current_state]['final']
    return is_accepted, current_state, transition_path

def get_transition_table():
    # Define the transition table as a list of dictionaries based on the provided image
    transitions = [
        {'current_state': 'q0', 'input_type': 'letter', 'next_state': 'q1', 'final': 'Yes'},
        {'current_state': 'q1', 'input_type': '=', 'next_state': 'q3', 'final': 'Yes'},
        {'current_state': 'q3', 'input_type': 'letter', 'next_state': 'q3', 'final': 'Yes'},
        {'current_state': 'q3', 'input_type': 'other', 'next_state': 'qErr', 'final': 'No'},
        {'current_state': 'qErr', 'input_type': 'letter', 'next_state': 'qErr', 'final': 'No'},
        {'current_state': 'qErr', 'input_type': 'other', 'next_state': 'qErr', 'final': 'No'},
    ]
    return transitions

# Recursive Predictive Parser
def parse_with_trace(tokens):
    pos = 0  # Position to track current token
    parse_trace = []  # To store the parsing trace as a list of strings
    
    def match(expected_type, expected_token=None):
        nonlocal pos, parse_trace
        if pos >= len(tokens):
            parse_trace.append(f"Expected {expected_type}{f' ({expected_token})' if expected_token else ''}, but reached end of input")
            return False
        token, token_type, _ = tokens[pos]
        if expected_token:
            matched = (token_type == expected_type and token == expected_token)
        else:
            matched = (token_type == expected_type)
        if matched:
            if token_type == 'identifier':
                parse_trace.append(f"Matched Identifier: {token}")
            elif token_type == 'operator':
                parse_trace.append(f"Matched Operator: {token}")
            elif token_type == 'semicolon':
                parse_trace.append(f"Matched Semicolon: {token}")
            elif token_type == 'number':
                parse_trace.append(f"Matched Number: {token}")
            pos += 1
            return True
        parse_trace.append(f"Failed: Expected {expected_type}{f' ({expected_token})' if expected_token else ''}, got {token_type} ({token})")
        return False
    
    def parse_statement():
        nonlocal pos, parse_trace
        if not match('identifier'):
            return False
        if not match('operator', '='):
            return False
        if not parse_expression():
            return False
        if not match('semicolon'):
            return False
        return True
    
    def parse_expression():
        nonlocal pos, parse_trace
        if not parse_term():
            return False
        if pos < len(tokens) and tokens[pos][0] == '+':
            if not match('operator', '+'):
                return False
            if not parse_term():
                return False
        return True
    
    def parse_term():
        nonlocal pos, parse_trace
        if pos >= len(tokens):
            return False
        token, token_type, _ = tokens[pos]
        if token_type == 'identifier' or token_type == 'number':
            match(token_type)
            return True
        elif token_type == 'parenthesis' and token == '(':
            match('parenthesis', '(')
            if not parse_expression():
                return False
            if not match('parenthesis', ')'):
                return False
            return True
        return False
    
    # Start parsing
    is_accepted = parse_statement()
    if is_accepted and pos < len(tokens):
        parse_trace.append("Failed: Extra tokens after statement")
        is_accepted = False
    
    return is_accepted, parse_trace

# Create the main window
root = tk.Tk()
root.title("Equation Scanner")
root.geometry("900x600")

# Add input field for the equation
tk.Label(root, text="Enter your code").pack(pady=20) # pack(pady=10) puts a space of 10 pixels above and below the text
entry = tk.Entry(root, width=50)
entry.pack(pady=10)

# Add Scan button with larger size and font
scan_button = tk.Button(root, text="Scan", command=scan_equation, width=15, height=2, font=("Arial", 14))
scan_button.pack(pady=10)

# Add label for parsing result
result_label = tk.Label(root, text="", font=("Arial", 12))
result_label.pack(pady=10)

# Create a Notebook for tabs
notebook = ttk.Notebook(root)
notebook.pack(pady=10, fill='both', expand=True)

# Create a style for the table to center text
style = ttk.Style()
style.configure("Treeview", font=("Arial", 10))
style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

# Create tab for Tokens
token_frame = ttk.Frame(notebook)
notebook.add(token_frame, text="Tokens")
tk.Label(token_frame, text="Tokens", font=("Arial", 12, "bold")).pack()
columns = ('Token', 'Type', 'Index')
token_table = ttk.Treeview(token_frame, columns=columns, show='headings', height=10)
token_table.heading('Token', text='Token', anchor='center')
token_table.heading('Type', text='Type', anchor='center')
token_table.heading('Index', text='Index', anchor='center')
token_table.column('Token', anchor='center', width=150)
token_table.column('Type', anchor='center', width=150)
token_table.column('Index', anchor='center', width=100)
token_table.tag_configure('odd', background='#FFFFFF')  # White for odd rows
token_table.tag_configure('even', background='#F0F0F0')  # Light gray for even rows
token_table.pack(pady=5, fill='both', expand=False)

# Create tab for Transition Table
transition_frame = ttk.Frame(notebook)
notebook.add(transition_frame, text="Transition Table")
tk.Label(transition_frame, text="Transition Table", font=("Arial", 12, "bold")).pack()
trans_columns = ('Current State', 'Input Type', 'Next State', 'Final State?')
transition_table = ttk.Treeview(transition_frame, columns=trans_columns, show='headings', height=10)
transition_table.heading('Current State', text='Current State', anchor='center')
transition_table.heading('Input Type', text='Input Type', anchor='center')
transition_table.heading('Next State', text='Next State', anchor='center')
transition_table.heading('Final State?', text='Final State?', anchor='center')
transition_table.column('Current State', anchor='center', width=150)
transition_table.column('Input Type', anchor='center', width=150)
transition_table.column('Next State', anchor='center', width=150)
transition_table.column('Final State?', anchor='center', width=150)
transition_table.tag_configure('odd', background='#FFFFFF')  # White for odd rows
transition_table.tag_configure('even', background='#F0F0F0')  # Light gray for even rows
transition_table.pack(pady=5, fill='both', expand=False)

# Create tab for Predictive Parser
parse_frame = ttk.Frame(notebook)
notebook.add(parse_frame, text="Predictive Parser")
tk.Label(parse_frame, text="Predictive Parser", font=("Arial", 12, "bold")).pack()
parse_text = tk.Text(parse_frame, height=10, width=50, font=("Arial", 10))
parse_text.pack(pady=5, fill='both', expand=True)

# Start the program
root.mainloop()