# Kizzy Bot

A Python-based automation tool for the Kizzy platform that handles betting on pools and spreads, as well as claiming rewards through browser automation.

## Overview

The Kizzy Bot is designed to automate various tasks on the Kizzy testnet platform, including:

- **Pool Betting**: Automatically places bets on Twitter and YouTube pools based on market dynamics
- **Spread Betting**: Calculates and places strategic bets on spread ranges (Twitter only)
- **Reward Claiming**: Automatically claims available mission rewards and cycle rewards
- **Multi-Account Support**: Can run multiple accounts simultaneously using different cookie files

## Features

### Betting Strategies

- **Pool Analysis**: Automatically determines whether to bet 'long' or 'short' based on existing pool positions
- **Spread Calculations**: Uses mathematical algorithms to calculate optimal bet amounts for spread ranges (Twitter only)
- **Risk Management**: Includes options to skip pools already bet on or bet on all available pools

### Automation Capabilities

- **Browser Automation**: Uses undetected ChromeDriver for reliable web interaction
- **Cookie Management**: Saves and loads authentication cookies to maintain sessions
- **Parallel Execution**: Supports running multiple accounts simultaneously
- **Error Handling**: Robust error handling with detailed logging

### Reward System

- **Mission Rewards**: Automatically claims available mission rewards
- **Cycle Rewards**: Claims cycle-based rewards when available
- **Multiple Attempts**: Retries reward claiming to ensure maximum collection

## Installation

### Prerequisites

- Python 3.7 or higher
- Google Chrome browser
- Poetry (for dependency management)

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/sebtheo/kizzy-selenium-automation.git
   cd kizzy-selenium-automation
   ```

2. Install dependencies using Poetry:

   ```bash
   make install
   ```

3. Run this command, enter the name of the account, then login to your Kizzy account in the browser window

   ```bash
   make save
   ```

4. If you have multiple files, rename the `kizzy/data/cookies.pkl` to `kizzy/data/<account_name>.pkl`

## Usage

### Running the bot

1. Run the bot using this command:

   ```bash
   make run
   ```

2. Choose your betting behaviour:

   - **Option 1**: Skip pools already bet on (conservative approach)
   - **Option 2**: Bet on all pools (including already bet on)

3. Choose execution mode:
   - **Option 1**: Run sequentially (one account at a time)
   - **Option 2**: Run in parallel (multiple accounts simultaneously)

### Cookie Management

- Cookie files are stored in `kizzy/data/` as `.pkl` files
- Each account should have its own cookie file
- The bot automatically detects and uses all available cookie files

## Configuration

### Betting Parameters

- **Pool Bet Amount**: Default 15 units per pool (enough for rewards)
- **Spread Bet Calculation**: Based on maximum odds and target payout
- **Wait Times**: 5 seconds between pool bets, 4 seconds between spread bets

### Platforms Supported

- **Twitter**: pools and spreads
- **YouTube**: pools only (no spreads)

Note: YouTube spreads are not available. The bot automatically skips fetching and processing spreads for YouTube.

## File Structure

```
kizzy/
├── main.py                 # Main bot implementation
├── data/                   # Cookie storage directory
│   ├── cookies.pkl         # Default cookie file
│   └── *.pkl               # Additional account cookies
└── save_cookies.py         # Cookie saving utility
```

## Technical Details

### Core Components

- **KizzyBot Class**: Main automation class handling all bot operations
- **Browser Management**: Undetected ChromeDriver for web automation
- **API Integration**: Direct API calls for betting and reward claiming
- **Session Management**: Cookie-based authentication persistence

### Betting Logic

- **Pool Side Selection**: Compares 'longs' vs 'shorts' to determine optimal betting side
- **Spread Calculations**: Uses mathematical formulas to calculate bet amounts based on odds
- **Position Tracking**: Maintains sets of already bet pool and spread IDs

### Error Handling

- **Network Errors**: Automatic retry mechanisms for failed API calls
- **Browser Errors**: Graceful handling of browser crashes and timeouts
- **Data Validation**: Robust parsing of API responses with fallback handling

## Safety Features

- **Rate Limiting**: Built-in delays between operations to avoid overwhelming the platform
- **Session Validation**: Verifies authentication before performing operations
- **Error Recovery**: Continues operation even if individual bets fail
- **Resource Cleanup**: Ensures browser instances are properly closed

## Troubleshooting

### Mismatch between Chrome version and ChromeDriver version

Error:

- `Message: session not created: cannot connect to chrome at 127.0.0.1:56001
from session not created: This version of ChromeDriver only supports Chrome version 139
Current browser version is 138.0.7204.184`

Resolution:

- The package `undetected-chromedriver` is used to attempt to bypass the bot protection. The browser is designed to auto-manage
  the driver for you, by using the latest chrome for best security and compatibility. However, if your local chrome is not up to date,
  you may need to go to [chrome://settings/help](chrome://settings/help) and update your chrome browser to the latest version.
- If you are using a different browser, you may need to install the correct version of the driver for your browser.

## Disclaimer

This tool is for educational and automation purposes only. Users are responsible for:

- Complying with Kizzy platform terms of service
- Managing their own risk and betting strategies
- Ensuring they have proper authorisation to use automated tools
- Understanding that automated betting carries financial risks

## Contributing

Contributions are welcome! Please ensure:

- Code follows existing style conventions
- New features include appropriate documentation
- Tests are added for new functionality
- British spelling is used in documentation

## License

This project is provided as-is for educational purposes. Users are responsible for compliance with applicable laws and platform terms of service.
