import undetected_chromedriver as uc
import pickle
import time
import os


def save_cookies():
    """
    Save cookies from the browser to a pickle file.
    """
    name = input("Enter the name of the account: ")
    driver = uc.Chrome()
    try:
        driver.get("https://testnet.kizzy.io/login")
        input(
            "\nPlease login manually in the browser window.\nOnce you're logged in, press Enter to continue..."
        )
        time.sleep(2)
        cookies = driver.get_cookies()
        os.makedirs("kizzy/data", exist_ok=True)
        with open(f"kizzy/data/{name}.pkl", "wb") as f:
            pickle.dump(cookies, f)
        print("Cookies saved successfully!")
    except Exception as e:
        print(f"Error occurred: {str(e)}")
    finally:
        driver.quit()


if __name__ == "__main__":
    save_cookies()
