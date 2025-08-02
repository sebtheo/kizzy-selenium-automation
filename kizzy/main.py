# Start of Selection
import undetected_chromedriver as uc
import time
import pickle
import os
import json
from typing import Dict, List, Set, Optional
import math
import glob
import threading


class KizzyBot:
    """
    KizzyBot automates betting and reward claiming on the Kizzy platform using browser automation.
    """

    def __init__(self, cookies_path: str = "kizzy/data/cookies.pkl"):
        """
        Initialise the KizzyBot instance.

        Args:
            cookies_path (str): Path to the cookies pickle file.
        """
        self.base_url = "https://testnet.kizzy.io"
        self.login_url = f"{self.base_url}/login"
        self.auth_endpoint = "/api/v2/auth"
        self.bet_endpoint = "/api/v2/place-bet"
        self.cookies_path = cookies_path
        self.driver = None
        self.pre_market_bet_ids: Set[int] = set()
        self.active_spread_bet_ids: Set[int] = set()
        self.rewards_base_url = "https://rest-api.kizzy.io"
        self.rewards_get_endpoint = "/app/reward?main_tab=missions"
        self.rewards_claim_endpoint = "/app/reward"

    def log(self, msg: str) -> None:
        """
        Print a timestamped log message.

        Args:
            msg (str): The message to log.
        """
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

    def start_browser(self) -> None:
        """
        Start a new undetected Chrome browser session and navigate to the login page.
        """
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        self.driver = uc.Chrome(options=chrome_options)
        self.log(f"Navigating to {self.login_url}")
        self.driver.get(self.login_url)

    def load_cookies(self) -> bool:
        """
        Load cookies from the specified pickle file and add them to the browser.

        Returns:
            bool: True if cookies were loaded successfully, False otherwise.
        """
        if not os.path.exists(self.cookies_path):
            return False
        try:
            with open(self.cookies_path, "rb") as f:
                cookies = pickle.load(f)
            for cookie in cookies:
                if "expiry" in cookie:
                    cookie["expiry"] = int(cookie["expiry"])
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    self.log(f"Failed to add cookie: {cookie.get('name')}, error: {e}")
            self.driver.refresh()
            self.log("Loaded cookies from file and refreshed page.")
            return True
        except Exception as e:
            self.log(f"Failed to load cookies: {e}")
            return False

    def manual_login(self) -> None:
        """
        Prompt the user to manually log in via the browser window.
        """
        input(
            "\nPlease login manually (Google OAuth) in the browser window.\nOnce you're logged in, press Enter to continue..."
        )
        time.sleep(2)

    def fetch_auth_data(self) -> Dict:
        """
        Fetch authentication data from the Kizzy API.

        Returns:
            Dict: The authentication data as a dictionary.
        """
        script = f"""
        return fetch("{self.auth_endpoint}", {{
            method: "GET",
            credentials: "include"
        }}).then(function(r) {{
            if (!r.ok) {{
                throw new Error("HTTP " + r.status + ": " + r.statusText);
            }}
            return r.text().then(function(text) {{
                try {{
                    return JSON.parse(text);
                }} catch (e) {{
                    throw new Error("Invalid JSON response: " + text.substring(0, 200) + "...");
                }}
            }});
        }});
        """
        try:
            return self.driver.execute_script(script)
        except Exception as e:
            self.log(f"Error fetching auth data: {e}")
            return {}

    def fetch_pools(self, platform: str) -> Dict:
        """
        Fetch pools for a given platform.

        Args:
            platform (str): The platform name (e.g., 'twitter', 'youtube').

        Returns:
            Dict: The pools data as a dictionary.
        """
        endpoint = f"/api/v2/pvp/{platform}"
        script = f"""
        return fetch("{endpoint}", {{
            method: "GET",
            credentials: "include"
        }}).then(function(r) {{
            if (!r.ok) {{
                throw new Error("HTTP " + r.status + ": " + r.statusText);
            }}
            return r.text().then(function(text) {{
                try {{
                    return JSON.parse(text);
                }} catch (e) {{
                    throw new Error("Invalid JSON response: " + text.substring(0, 200) + "...");
                }}
            }});
        }});
        """
        try:
            return self.driver.execute_script(script)
        except Exception as e:
            self.log(f"Error fetching {platform} pools: {e}")
            return {}

    def place_bet(self, pool_id: int, side: str, amount: int = 15) -> Dict:
        """
        Place a bet on a given pool.

        Args:
            pool_id (int): The pool ID.
            side (str): The side to bet on ('long' or 'short').
            amount (int): The amount to bet.

        Returns:
            Dict: The result of the bet as a dictionary.
        """
        payload = {"amount": amount, "parimutuelPoolID": pool_id, "side": side}
        script = f"""
        return fetch("https://rest-api.kizzy.io/app/place-bet-pvp/{pool_id}", {{
            method: "POST",
            credentials: "include",
            headers: {{
                "accept": "*/*",
                "content-type": "application/json"
            }},
            body: JSON.stringify({json.dumps(payload)})
        }}).then(function(r) {{
            if (!r.ok) {{
                throw new Error("HTTP " + r.status + ": " + r.statusText);
            }}
            return r.text().then(function(text) {{
                try {{
                    return JSON.parse(text);
                }} catch (e) {{
                    throw new Error("Invalid JSON response: " + text.substring(0, 200) + "...");
                }}
            }});
        }});
        """
        try:
            return self.driver.execute_script(script)
        except Exception as e:
            self.log(f"Error placing bet on pool {pool_id}: {e}")
            return {"success": False, "error": str(e)}

    def fetch_spreads(self, platform: str) -> Dict:
        """
        Fetch spreads for a given platform.

        Args:
            platform (str): The platform name.

        Returns:
            Dict: The spreads data as a dictionary.
        """
        endpoint = f"/api/v2/spreads/{platform}"
        script = f"""
        return fetch("{endpoint}", {{
            method: "GET",
            credentials: "include"
        }}).then(function(r) {{
            if (!r.ok) {{
                throw new Error("HTTP " + r.status + ": " + r.statusText);
            }}
            return r.text().then(function(text) {{
                try {{
                    return JSON.parse(text);
                }} catch (e) {{
                    throw new Error("Invalid JSON response: " + text.substring(0, 200) + "...");
                }}
            }});
        }});
        """
        try:
            return self.driver.execute_script(script)
        except Exception as e:
            self.log(f"Error fetching {platform} spreads: {e}")
            return {}

    def place_spread_bet(self, spread_range_id: int, amount: int) -> Dict:
        """
        Place a bet on a spread range using multipart/form-data.

        Args:
            spread_range_id (int): The spread range ID.
            amount (int): The amount to bet.

        Returns:
            Dict: The result of the bet as a dictionary.
        """
        script = f"""
        var formData = new FormData();
        formData.append("spreadPoolRangeID", "{spread_range_id}");
        formData.append("amount", "{amount}");
        return fetch("https://testnet.kizzy.io/api/v2/place-bet/spread", {{
            method: "POST",
            credentials: "include",
            body: formData
        }}).then(function(r) {{
            if (!r.ok) {{
                throw new Error("HTTP " + r.status + ": " + r.statusText);
            }}
            return r.text().then(function(text) {{
                try {{
                    return JSON.parse(text);
                }} catch (e) {{
                    throw new Error("Invalid JSON response: " + text.substring(0, 200) + "...");
                }}
            }});
        }});
        """
        try:
            return self.driver.execute_script(script)
        except Exception as e:
            self.log(f"Error placing spread bet on range {spread_range_id}: {e}")
            return {"success": False, "error": str(e)}

    def process_spreads(self, platform: str) -> None:
        """
        Fetch and process spreads for a platform, calculating and placing bets.

        Args:
            platform (str): The platform name.
        """
        spreads_data = self.fetch_spreads(platform)
        self.log(f"Fetched {platform} spreads: {json.dumps(spreads_data)[:200]}...")
        spreads = (
            spreads_data.get("spreadsData", [])
            if isinstance(spreads_data, dict)
            else []
        )

        for spread in spreads:
            spread_id = spread.get("ID")
            self.log(f"Processing spread {spread_id}: {spread.get('title')}")

            spread_ranges = spread.get("spreadRanges")
            if not spread_ranges:
                self.log(f"No spread ranges for spread {spread_id}, skipping.")
                continue

            max_odds = 0.0
            for r in spread_ranges:
                if r.get("odds") and r["odds"] > max_odds:
                    max_odds = r["odds"]

            if max_odds == 0.0:
                self.log(
                    f"Could not determine max odds for spread {spread_id}, skipping."
                )
                continue

            target_payout = 15 * max_odds
            self.log(f"Max odds: {max_odds:.2f}, target payout: {target_payout:.2f}")

            bets_to_place = []
            total_bet_amount = 0

            for idx, r in enumerate(spread_ranges):
                odds = r.get("odds")
                if odds and odds > 0:
                    bet_amount = math.ceil(target_payout / odds)
                    if bet_amount > 99:
                        bet_amount = 99
                    # For 4th and 6th bets, subtract 5 (but not below 1)
                    if idx == 3 or idx == 5:
                        bet_amount = max(1, bet_amount - 5)
                    bets_to_place.append(
                        {"range_id": r["id"], "amount": bet_amount, "odds": odds}
                    )
                    total_bet_amount += bet_amount

            self.log(f"Calculated bets for spread {spread_id}:")
            for bet in bets_to_place:
                self.log(
                    f"  Range ID: {bet['range_id']}, Amount: {bet['amount']}, Odds: {bet['odds']:.2f}"
                )
            self.log(f"Total bet amount for this spread: {total_bet_amount}")

            for bet in bets_to_place:
                if bet["range_id"] in self.active_spread_bet_ids:
                    self.log(
                        f"Skipping bet on range {bet['range_id']}, already placed."
                    )
                    continue

                self.log(
                    f"Placing bet of {bet['amount']} on range {bet['range_id']} (odds={bet['odds']})"
                )
                try:
                    result = self.place_spread_bet(bet["range_id"], bet["amount"])
                    self.log(f"Bet result for range {bet['range_id']}: {result}")
                    if result.get("success"):
                        self.active_spread_bet_ids.add(bet["range_id"])
                except Exception as e:
                    self.log(
                        f"Error placing spread bet on range {bet['range_id']}: {e}"
                    )
                time.sleep(4)  # Wait between bets

            time.sleep(5)  # Wait between processing spreads

    def update_active_positions(self) -> None:
        """
        Update the sets of pre-market and active spread bet IDs from authentication data.
        """
        auth_data = self.fetch_auth_data()
        if isinstance(auth_data, dict):
            self.pre_market_bet_ids = set(auth_data.get("preMarketBetIDs", []))
            self.active_spread_bet_ids = set(
                auth_data.get("activeSpreadRangesPositionsIDS", [])
            )
        else:
            self.pre_market_bet_ids = set()
            self.active_spread_bet_ids = set()
        self.log(f"Current preMarketBetIDs: {self.pre_market_bet_ids}")
        self.log(
            f"Current activeSpreadRangesPositionsIDS: {self.active_spread_bet_ids}"
        )

    def determine_bet_side(self, pool: Dict) -> str:
        """
        Determine which side to bet on for a pool.

        Args:
            pool (Dict): The pool data.

        Returns:
            str: 'long' if longs > shorts, otherwise 'short'.
        """
        longs = float(pool.get("longs", 0))
        shorts = float(pool.get("shorts", 0))
        return "long" if longs > shorts else "short"

    def process_pools(self, platform: str, skip_existing_bets: bool = True) -> None:
        """
        Process pools for a platform, placing bets as appropriate.

        Args:
            platform (str): The platform name.
            skip_existing_bets (bool): Whether to skip pools already bet on.
        """
        pools_data = self.fetch_pools(platform)
        self.log(f"Fetched {platform} pools: {json.dumps(pools_data)[:200]}...")
        pools = pools_data.get("poolsData", []) if isinstance(pools_data, dict) else []
        for pool in pools:
            pool_id = pool.get("ID")
            if skip_existing_bets and pool_id in self.pre_market_bet_ids:
                self.log(f"Skipping {platform} pool {pool_id}: already bet")
                continue
            longs = float(pool.get("longs", 0))
            shorts = float(pool.get("shorts", 0))
            side = self.determine_bet_side(pool)
            self.log(
                f"{platform.title()} pool {pool_id}: Betting 15 on {side.upper()} (longs={longs}, shorts={shorts})"
            )
            bet_result = self.place_bet(pool_id, side)
            self.log(f"Bet result for {platform} pool {pool_id}: {bet_result}")
            time.sleep(5)  # Wait between bets

    def get_rewards(self) -> List[Dict]:
        """
        Fetch available missions with rewards from the rewards endpoint.

        Returns:
            List[Dict]: A list of missions with reward information.
        """
        script = f"""
        return fetch("{self.rewards_base_url}{self.rewards_get_endpoint}", {{
            method: "GET",
            credentials: "include"
        }}).then(function(r) {{
            if (!r.ok) {{
                throw new Error("HTTP " + r.status + ": " + r.statusText);
            }}
            return r.text().then(function(text) {{
                try {{
                    return JSON.parse(text);
                }} catch (e) {{
                    throw new Error("Invalid JSON response: " + text.substring(0, 200) + "...");
                }}
            }});
        }});
        """
        try:
            result = self.driver.execute_script(script)
        except Exception as e:
            self.log(f"Error fetching rewards: {e}")
            return []
        self.log(f"Fetched rewards: {json.dumps(result)[:200]}...")
        missions = []
        if not isinstance(result, dict):
            self.log("Error parsing missions: result is not a dict")
            return missions
        data = result.get("data")
        if not isinstance(data, dict):
            self.log("Error parsing missions: 'data' is not a dict")
            return missions
        missions = data.get("missions", [])
        cycle_data = data.get("cycleData", {})
        if isinstance(cycle_data, dict) and cycle_data.get("released", False):
            cycle_id = cycle_data.get("ID", 0)
            for mission in missions:
                # Attach both the global cycleDataID and the per-mission metrics.cycleID if present
                mission["cycleDataID"] = cycle_id
                # If mission.metrics.cycleID is missing, set it to the global cycle_id
                if "metrics" not in mission or not isinstance(mission["metrics"], dict):
                    mission["metrics"] = {}
                if (
                    "cycleID" not in mission["metrics"]
                    or not mission["metrics"]["cycleID"]
                ):
                    mission["metrics"]["cycleID"] = cycle_id
        return missions

    def claim_rewards(self, missions: Optional[List[Dict]] = None) -> None:
        """
        Claim all available rewards for missions where claimEnabled and not claimed.

        Args:
            missions (Optional[List[Dict]]): List of missions to claim rewards for. If None, fetches rewards.
        """
        if missions is None:
            missions = self.get_rewards()

        # First, try to claim the cycle if available
        cycle_id = None
        if missions and len(missions) > 0:
            # Try to get cycleID from the first mission
            if "metrics" in missions[0] and isinstance(missions[0]["metrics"], dict):
                cycle_id = missions[0]["metrics"].get("cycleID")
            if not cycle_id:
                cycle_id = missions[0].get("cycleDataID")

        if cycle_id:
            self.log(f"Attempting to claim cycle {cycle_id}")
            cycle_payload = {
                "_action": "claim-cycle",
                "missionCredID": 0,
                "cycleID": cycle_id,
            }
            script = f"""
            return fetch("{self.rewards_base_url}{self.rewards_claim_endpoint}", {{
                method: "POST",
                credentials: "include",
                headers: {{
                    "accept": "*/*",
                    "content-type": "application/json"
                }},
                body: JSON.stringify({json.dumps(cycle_payload)})
            }}).then(function(r) {{
                if (!r.ok) {{
                    throw new Error("HTTP " + r.status + ": " + r.statusText);
                }}
                return r.text().then(function(text) {{
                    try {{
                        return JSON.parse(text);
                    }} catch (e) {{
                        throw new Error("Invalid JSON response: " + text.substring(0, 200) + "...");
                    }}
                }});
            }});
            """
            try:
                result = self.driver.execute_script(script)
                self.log(f"Cycle claim result: {result}")
            except Exception as e:
                self.log(f"Error claiming cycle {cycle_id}: {e}")
            time.sleep(2)

        # Then claim individual mission rewards
        claimable = [
            m for m in missions if m.get("claimEnabled") and not m.get("claimed")
        ]
        if not claimable:
            self.log("No claimable mission rewards found.")
            return
        for mission in claimable:
            mission_id = mission.get("id")
            # Try to get the correct cycleID: prefer mission['metrics']['cycleID'], fallback to mission['cycleDataID']
            cycle_id = 0
            if "metrics" in mission and isinstance(mission["metrics"], dict):
                cycle_id = mission["metrics"].get("cycleID", 0)
            if not cycle_id:
                cycle_id = mission.get("cycleDataID", 0)
            payload = {
                "_action": "claim-mission-rewards",
                "missionCredID": mission_id,
                "cycleID": cycle_id,
            }
            script = f"""
            return fetch("{self.rewards_base_url}{self.rewards_claim_endpoint}", {{
                method: "POST",
                credentials: "include",
                headers: {{
                    "accept": "*/*",
                    "content-type": "application/json"
                }},
                body: JSON.stringify({json.dumps(payload)})
            }}).then(function(r) {{
                if (!r.ok) {{
                    throw new Error("HTTP " + r.status + ": " + r.statusText);
                }}
                return r.text().then(function(text) {{
                    try {{
                        return JSON.parse(text);
                    }} catch (e) {{
                        throw new Error("Invalid JSON response: " + text.substring(0, 200) + "...");
                    }}
                }});
            }});
            """
            try:
                result = self.driver.execute_script(script)
                self.log(
                    f"Claimed reward for mission {mission_id} (cycleID={cycle_id}): {result}"
                )
            except Exception as e:
                self.log(f"Error claiming reward for mission {mission_id}: {e}")
            time.sleep(2)

    def set_tutorial_flags_to_true(self) -> None:
        """
        Set localStorage tutorial flags to true for Home, Mission, Profile, Pvp, and Spreads.
        """
        script = """
        ["Home", "Mission", "Profile", "Pvp", "Spreads"].forEach(function(key) {
            localStorage.setItem(key + "Tutorial", "true");
        });
        """
        if self.driver:
            self.driver.execute_script(script)

    def run_betting_once(
        self,
        platforms: List[str] = ["twitter", "youtube"],
        skip_existing_bets: bool = True,
    ) -> None:
        """
        Run the betting and reward claiming process once for the specified platforms.

        Args:
            platforms (List[str]): List of platform names to process.
            skip_existing_bets (bool): Whether to skip pools already bet on.
        """
        try:
            self.start_browser()
            self.set_tutorial_flags_to_true()
            if not self.load_cookies():
                self.manual_login()
            self.update_active_positions()
            for platform in platforms:
                self.log(f"Processing {platform} pools...")
                self.process_pools(platform, skip_existing_bets)
                self.log(f"Processing {platform} spreads...")
                self.process_spreads(platform)
            self.log("Checking for claimable rewards...")
            for x in range(5):
                missions = self.get_rewards()
                self.claim_rewards(missions)
                time.sleep(2)
        except Exception as e:
            self.log(f"Error: {e}")
        finally:
            self.close()

    def close(self) -> None:
        """
        Close the browser session if it is open.
        """
        if self.driver:
            self.driver.quit()
            self.log("Browser closed.")


def run_bot_with_cookies(pkl_file: str, skip_existing_bets: bool = True) -> None:
    """
    Run the bot with a specific cookie file.

    Args:
        pkl_file (str): Path to the pickle file containing cookies.
        skip_existing_bets (bool): Whether to skip pools already bet on.
    """
    try:
        print(f"\n=== Running bot with cookies: {pkl_file} ===")
        bot = KizzyBot(cookies_path=pkl_file)
        bot.run_betting_once(
            platforms=["twitter", "youtube"], skip_existing_bets=skip_existing_bets
        )
    except Exception as e:
        print(f"Error running bot with {pkl_file}: {e}")
    finally:
        # Ensure browser is closed even if there's an error
        if "bot" in locals() and hasattr(bot, "driver") and bot.driver:
            try:
                bot.driver.quit()
            except Exception as e:
                print(f"Error closing browser: {e}")
                pass


def main():
    """
    Main entry point for running the KizzyBot on all available cookie files.
    Prompts the user for betting and execution mode preferences.
    """
    pkl_files = glob.glob("kizzy/data/*.pkl")

    if not pkl_files:
        print("No .pkl files found in kizzy/data/ directory.")
        return

    print(f"Found {len(pkl_files)} cookie files:")
    for i, pkl_file in enumerate(pkl_files, 1):
        print(f"{i}. {pkl_file}")

    # Ask about betting behaviour
    while True:
        bet_choice = input(
            "\nChoose betting behaviour:\n1. Skip pools already bet on (default)\n2. Bet on all pools (including already bet on)\nEnter 1 or 2: "
        ).strip()

        if bet_choice == "1":
            skip_existing_bets = True
            print("Will skip pools already bet on.")
            break
        elif bet_choice == "2":
            skip_existing_bets = False
            print("Will bet on all pools (including already bet on).")
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

    while True:
        choice = input(
            "\nChoose execution mode:\n1. Run sequentially\n2. Run in parallel\nEnter 1 or 2: "
        ).strip()

        if choice == "1":
            print("\n=== Running sequentially ===")
            for pkl_file in pkl_files:
                run_bot_with_cookies(pkl_file, skip_existing_bets)
            break
        elif choice == "2":
            print("\n=== Running in parallel ===")
            threads = []
            for pkl_file in pkl_files:
                thread = threading.Thread(
                    target=run_bot_with_cookies, args=(pkl_file, skip_existing_bets)
                )
                threads.append(thread)
                thread.start()
                # Small delay to prevent ChromeDriver conflicts
                time.sleep(2)

            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            print("\n=== All parallel executions completed ===")
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")


if __name__ == "__main__":
    main()
# End of Selection
