import os
import requests
from tabulate import tabulate
from concurrent.futures import ThreadPoolExecutor, as_completed

# Color codes for console output
blue = "\033[94m"
red = "\033[91m"
yellow = "\033[93m"
green = "\033[92m"
white = "\033[97m"

# Logos for display
logo1 = """
 __      __      .__   _____  __      __                       
/  \    /  \____ |  |_/ ____\/  \    /  \_____ _______   ____  
\   \/\/   /  _ \|  |\   __\ \   \/\/   /\__  \\_  __ \_/ __ \ 
 \        (  <_> )  |_|  |    \        /  / __ \|  | \/\  ___/ 
  \__/\  / \____/|____/__|     \__/\  /  (____  /__|    \___  >
       \/                           \/        \/            \/                                                                       
"""
logo2 = """
__________                                      _________ .__                   __                 
\______   \_______  _______  ______.__.         \_   ___ \|  |__   ____   ____ |  | __ ___________ 
 |     ___/\_  __ \/  _ \  \/  <   |  |  ______ /    \  \/|  |  \_/ __ \_/ ___\|  |/ // __ \_  __ \\
 |    |     |  | \(  <_> >    < \___  | /_____/ \     \___|   Y  \  ___/\  \___|    <\  ___/|  | \/
 |____|     |__|   \____/__/\_ \/ ____|          \______  /___|  /\___  >\___  >__|_ \\___  >__|   
                              \/\/                      \/     \/     \/     \/     \/    \/            
"""

txtin = r'.\input.txt'
txtout = r'.\output.txt'
delay = 5000  # Default timeout in milliseconds - Increase if too many proxies are unsuccessful
max_threads = 50  # Maximum number of threads

def check_proxy(proxy, delay):
    """Checks if a proxy is working."""
    proxies = {"http": proxy, "https": proxy}
    try:
        response = requests.get("https://www.google.com", proxies=proxies, timeout=delay)
        return proxy, response.status_code == 200
    except requests.exceptions.RequestException:
        return proxy, False

def clear_console():
    """Clears the console."""
    os.system('cls' if os.name == 'nt' else 'printf "\033c"')

def update_table(proxies, successful_proxies, unsuccessful_proxies):
    """Updates the table with current proxy statistics."""
    remaining_proxies = len(proxies) - len(successful_proxies) - len(unsuccessful_proxies)
    successful_count = len(successful_proxies)
    unsuccessful_count = len(unsuccessful_proxies)

    return tabulate([
        [yellow + f"Total Proxies: " + white, yellow + str(len(proxies)) + white],
        [green + f"Successful Proxies: " + white, green + str(successful_count) + white],
        [red + f"Unsuccessful Proxies: " + white, red + str(unsuccessful_count) + white],
        [blue + f"Remaining Proxies: " + white, blue + str(remaining_proxies) + white],
    ], headers=["Output", "Status"], tablefmt="pretty")

def get_user_input():
    """Prompts the user for input files and timeout."""
    global txtin, txtout, delay, max_threads

    clear_console()
    print(red + logo1)
    print(logo2)
    print("")

    switchin = input(white + "The default import file is: " + yellow + txtin + white + ". Do you want to change it? (y/n): ")
    if switchin.lower() == "y":
        txtin = input(yellow + "Please enter new import file: ")

    switchout = input(white + "The default export file is: " + yellow + txtout + white + ". Do you want to change it? (y/n): ")
    if switchout.lower() == "y":
        txtout = input("Please enter new export file: ")
        
    switchthreads = input(white + "The default thread count is: " + yellow + str(max_threads) + white + ". Do you want to change it? (y/n): ")
    if switchthreads.lower() == "y":
        max_threads = input("Please enter new thread count: ")

    delay_input = input(white + "The default timeout is: " + yellow + str(delay) + "ms." + white + " Do you want to change it? (y/n): ")
    if delay_input.lower() == "y":
        try:
            delay = float(input("Please enter new timeout in milliseconds: ")) / 1000  # Convert to seconds
        except ValueError:
            print(red + "Invalid input. Using default timeout." + white)
            delay = 5  # Default timeout in seconds
    else:
        delay = delay / 1000  # Convert to seconds

def main():
    """Main function of the program."""
    get_user_input()

    with open(txtin, "r") as f:
        proxies = [line.strip() for line in f.readlines()]

    successful_proxies = []
    unsuccessful_proxies = []

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(check_proxy, proxy, delay): proxy for proxy in proxies}

        for future in as_completed(futures):
            proxy, result = future.result()
            clear_console()
            print(red + logo1)
            print(logo2 + white)
            print(update_table(proxies, successful_proxies, unsuccessful_proxies))
            print("")
            print(yellow + "Currently checking: ", blue + str(proxy) + white)
            if result:
                successful_proxies.append(proxy)
            else:
                unsuccessful_proxies.append(proxy)

    clear_console()
    print(red + logo1)
    print(logo2 + white)
    print(update_table(proxies, successful_proxies, unsuccessful_proxies))
    print("")
    print("")
    print(yellow + "Writing working proxies into output.txt... ", end="")

    with open(txtout, "a") as f:
        for proxy in successful_proxies:
            f.write(proxy + "\n")
    print(green + "Done.")

    print(yellow + "Checking for duplicates in output.txt...   ", end="")

    with open(txtout, "r+") as f:
        lines = f.readlines()
        f.seek(0)
        f.truncate()
        for line in set(lines):
            f.write(line)
    print(green + "Done.")
    print("")
    input(yellow + "Please press Enter to exit ProxyChecker... ")

if __name__ == "__main__":
    main()