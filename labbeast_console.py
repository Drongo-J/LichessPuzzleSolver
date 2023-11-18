from asyncio import sleep
import subprocess
import os
import re
import pygetwindow as gw
import pyautogui
import time
import pyperclip
from bs4 import BeautifulSoup

def print_color(text, color):
    colors = {
        "RED": "\033[91m",
        "GREEN": "\033[92m",
        "CYAN": "\033[96m",
        "RESET": "\033[0m",
        "YELLOW": "\033[93m"
    }
    return f"{colors[color]}{text}{colors['RESET']}"

def enter_move(move):
    pyperclip.copy(move)
    
    pyautogui.click(900, 1000)

    # Focus on Keyboard Move Input 
    pyautogui.press('enter')

    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('del')

    pyautogui.hotkey('ctrl', 'v')
    
    time.sleep(0.1)
    pyautogui.press('enter')

def get_and_show_chess_moves(moves):
    # Use regular expression to find move numbers and corresponding moves
    move_pattern = re.compile(r'(\d+\.)')
    split_moves = re.split(move_pattern, moves)[1:]

    # Group the move numbers and moves together
    move_groups = [f'{split_moves[i]} {split_moves[i+1]}' for i in range(0, len(split_moves), 2)]

    first_part_color = ''
    second_part_color = ''
    my_move_index = 0    
    if move_groups[0].split(' ')[1].strip() == '..':
        first_part_color = 'RED'
        second_part_color= 'GREEN'
        my_move_index = 2
    else:
        first_part_color = 'GREEN'
        second_part_color = 'RED'
        my_move_index = 1
        
    new_arr = []
    moves = []
    for move in move_groups:
        print(move)
        move_items = [item.strip() for item in move.split(' ') if item.strip()]
        move = f"{print_color(move_items[0], 'CYAN')} {print_color(move_items[1], first_part_color)}"
        # Check if move_items has at least three elements before including the third part
        if len(move_items) >= 3:
            if (move_items[2] == '*'):
                move += f" {print_color(move_items[2], 'RESET')}"
            else:
                move += f" {print_color(move_items[2], second_part_color)}"
            
        moves.append(move_items[my_move_index])
        new_arr.append(move)

    # Print the result
    result_string = '\n'.join(new_arr)
    
    print(print_color("Solution: \n", "CYAN") + result_string + '\n\n')
    
    return moves

def run_labbeast(user_input):
    # Update the Labbeast executable path using a raw string (r'')
    labbeast_exe_path = r'Labbeast - Lichess Puzzle Extractor.exe'

    try:
        # Write user input to input.txt
        with open('input.txt', 'w') as input_file:
            input_file.write(user_input)

        # Run Labbeast with input
        process = subprocess.Popen([labbeast_exe_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        output, _ = process.communicate(input=user_input)

        # Explicitly open and read the content of output.pgn
        with open('output.pgn', 'r') as pgn_file:
            lines = pgn_file.readlines()

        # Print the content of output.pgn with colored moves
        print(print_color("\nContent of output.pgn:", "CYAN"))
        for line in lines[:-2]:
            print(line, end = '')  # Print all lines except the last two, add newline
        # Highlight the second-to-last line in a different color
        moves = get_and_show_chess_moves(lines[-2])
        for move in moves:
            enter_move(move.replace("x", "").replace("+", ""))

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Labbeast executable not found. Please check the file path.")

def switch_to_lichess_tab():
    print(print_color("\nSearching for Lichess Training Tab . . .", "YELLOW"))
    try:
        tabs_to_search = 10  

        for _ in range(tabs_to_search):
            # Get the active window
            active_window = gw.getActiveWindow()

            if not active_window:
                print_color("No active window found.", "RED")
                return False

            # Get the title of the current tab
            current_tab_title = active_window.title.lower()

            # Check if the title contains "lichess"
            if "lichess" in current_tab_title:
                print(print_color("Found Lichess Tab", "GREEN"))
                
                #pyautogui.hotkey('ctrl', 'r') 
                #time.sleep(3)  # Give it some time to refresh                

                return True  # Successfully switched to the Lichess tab        

            # Send Ctrl+Tab to switch between tabs
            pyautogui.hotkey('ctrl', 'tab')
            time.sleep(1)  # Wait for a short time to allow the tab switch to take effect

        # If the "lichess" tab is not found, open a new tab with the specified URL
        print(print_color("Didn't find Lichess Training Tab. Creating New One.", "YELLOW"))
        pyautogui.hotkey('ctrl', 't')  # Open a new tab
        time.sleep(1)
        pyautogui.write('https://lichess.org/training/mix')
        pyautogui.press('enter')

        return True

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

def get_html_of_lichess_tab(edge_window, c):
    try:
        edge_window.activate()
            
        if first_time:
            time.sleep(1)
        
            success = switch_to_lichess_tab()
    
            if not success:
                print("Lichess Tab not found.")
                return None
        
        # Wait for a short time to allow the page source to load
        time.sleep(1)
         
        pyautogui.click(916, 1004)

        # Send Ctrl+A to select all
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'a')
        
        time.sleep(0.5)

        # Send Ctrl+C to copy the selected content
        pyautogui.hotkey('ctrl', 'c')
        pyautogui.hotkey('ctrl', 'c')

        # Get the clipboard content
        html_content = pyperclip.paste()

        # Close the tab (you may need to customize this based on the browser)
        #pyautogui.hotkey('ctrl', 'w')

        # Bring the Edge window to the foreground
        edge_window.activate()

        return html_content

    except Exception as e:
        print(print_color(f"An error occurred: {str(e)}", "RED"))
        return None

def get_puzzle_id(text):
    puzzle_id_length = 5
    try:
        # Find the index of 'Puzzle #' in the string
        hash_index = text.find('#')
        
        # If '#' is found, extract the substring starting with '#' and containing the first 5 letters
        if hash_index != -1:
            result = text[hash_index + 1:hash_index + puzzle_id_length + 1]
            return result
        else:
            # If '#' is not found, return an empty string
            return ""
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
    

if __name__ == "__main__":
    # Get all open windows
    all_windows = gw.getAllWindows()

    # Find the Edge browser window by checking the title
    edge_window = None
    cmd_window = None

    # Find the Edge browser window by checking the title
    for window in all_windows:
        if "Edge" in window.title:
            edge_window = window
        elif "cmd.exe" in window.title:
            cmd_window = window

  
    # Check if Edge browser window is found
    if not edge_window:
        print(print_color("Edge browser window not found. Exiting.", "RED"))
        os._exit(1)  # Exit with an error code
    else:
        print(print_color("Found Edge Browser window.", "GREEN"))
        time.sleep(1)
        edge_window.activate()
        edge_window.maximize()
        print(print_color("Moving Edge Browser window to the left of the screen.", "YELLOW"))
        time.sleep(1)
        pyautogui.hotkey('winleft', 'left')
        pyautogui.press('esc')

    # Check if Command Prompt window is found
    if not cmd_window:
        print(print_color("Command Prompt window not found. Exiting.", "RED"))
        os._exit(1)  # Exit with an error code
    else:
        print(print_color("Found Command Prompt window", "GREEN"))
        time.sleep(1)
        cmd_window.activate()
        cmd_window.maximize()
        print(print_color("Moving Command Prompt window to the right of the screen.", "YELLOW"))
        time.sleep(1)
        pyautogui.hotkey('winleft', 'right')
        pyautogui.press('esc')
            
    puzzles_solved = 0
    first_time = True
    while True:
        # Fetch HTML of the Lichess tab in the Edge browser window
        html = get_html_of_lichess_tab(edge_window, first_time)
        first_time = False
        print(" ")
        if html:
            # Extract puzzle ID from HTML
            print(print_color("Searching for ID of Puzzle . . .", "YELLOW"))
            puzzle_id = get_puzzle_id(html)
            print(print_color("Puzzle ID:", "CYAN"), print_color(puzzle_id, "YELLOW"))

            # Get user input
            # user_input = input("Enter Puzzle ID (or type 'exit' to end): ")
            # my_input = user_input
            my_input = puzzle_id

            if my_input.lower() == 'exit':
                break
            
            if len(my_input) != 5:
                print(print_color("Invalid Puzzle ID! Exiting.", "RED"))
                break

            # Run Labbeast with the puzzle ID
            print("Running Labbeast for puzzle:", my_input)
            
            run_labbeast(my_input)
            puzzles_solved += 1

            print(print_color(f"Puzzles Solved: {puzzles_solved}", "GREEN"))
            print(print_color("Waiting for other puzzle . . .", "YELLOW"))
            time.sleep(1.5) 
        else:
            print(print_color("Error fetching HTML of Lichess Tab. Exiting.", "RED"))
            os._exit(1)
