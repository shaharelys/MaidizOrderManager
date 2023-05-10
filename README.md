# Cibus Order Manager

Cibus Order Manager is an automated system designed to manage food orders from the Cibus website. The system scrapes order data, processes it, and manages customer contacts using the Google People API. It also controls display function for the crew and printing functions for the site printers.

## Features

- Automatically logs in to the Cibus website and navigates to the orders page.
- Monitors the website for new orders and extracts order data.
- Checks if the customer is already in the database and updates their details or creates a new customer.
- Creates and updates customer contacts using the Google People API.
- Assigns orders to a trip.
- Sends order confirmation SMS to customers.
- Prevents computer from going to sleep while the program is running.
- Alerts the user if the order amount is below a certain threshold.

## Installation

1. Clone this repository or download the source code.
2. Install the required dependencies by running `pip install -r requirements.txt` in your project directory.
3. Set up the necessary API keys and credentials (Google People API, SMS service, etc.).
4. Update the configuration details in the project, such as login credentials and URL.

## Usage

1. Run the main.py script to start the Cibus Order Manager.
2. The script will automatically log in to the Cibus website, navigate to the orders page, and start processing new orders.
3. To stop the script, press Ctrl+C in the terminal or command prompt.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
