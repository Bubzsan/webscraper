from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import spacy
import os
import time

# Constants
BASE_URL = "https://www.metaculus.com"
URL = BASE_URL + "/questions/?status=open&has_group=false&topic=ai&type=forecast&order_by=-activity"
SCORE_THRESHOLD = 2000
excel_file = 'metaculus_sample.xlsx'
MAX_CLICKS = int(os.getenv("SEARCH_POWER"))  # Maximum number of times to click the 'Load More' button
LOAD_MORE_BUTTON = ".button-row button"  # CSS selector for the 'Load More' button
SCROLL_PAUSE_TIME = 2  # Time to wait for content to load after clicking


def get_relevant_cards(url, score_threshold):

    print(MAX_CLICKS)
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.binary_location = os.getenv('CHROME_BINARY_PATH')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36")
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode (without a GUI).
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize the WebDriver using the Chrome options
    driver = webdriver.Chrome(options=chrome_options)

    # Navigate to the page
    driver.get(URL)

    # Wait to load page
    time.sleep(2)

    # Loads more content into the page by clicking the Load More button
    try:
        for _ in range(MAX_CLICKS):
            # Wait for the 'Load More' button to be clickable
            load_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, LOAD_MORE_BUTTON))
            )
            
            # Click the 'Load More' button
            load_more_button.click()
            
            # Wait for the content to load
            time.sleep(SCROLL_PAUSE_TIME)
            
            # Check if the 'Load More' button is still visible
            if not driver.find_elements(By.CSS_SELECTOR, LOAD_MORE_BUTTON):
                print("No more content to load.")
                break
    except Exception as e:
        print(f"An exception occurred: {e}")

    # Fetch the question cards data
    question_cards = driver.execute_script("""
        const BASE_URL = arguments[0];
        const currentYear = new Date().getFullYear();
        const tenYearsFromNow = currentYear + 10;

        return Array.from(document.querySelectorAll('.question_card')).map(card => {
            const hrefElement = card.querySelector('.question_card__main_container a');
            const predictionChip = card.querySelector('.question_card__stats__chip-row');
            const statusElement = card.querySelector('.question_card_footer__right question-status div span');
            
            const predictionText = predictionChip ? predictionChip.textContent.trim() : '';
            const containsPercentage = predictionText.includes('%');
            const statusText = statusElement ? statusElement.textContent.trim() : '';
            
            const yearMatch = statusText.match(/Closes\s+\w+\s+\d+,\s+(\d{4})/);
            const closingYear = yearMatch ? parseInt(yearMatch[1]) : null;
            const evergreen = closingYear && (closingYear >= tenYearsFromNow);

            if (containsPercentage) {
                return {
                    'Url': hrefElement ? BASE_URL + hrefElement.getAttribute('href') : null,
                    'Narrative': hrefElement ? hrefElement.textContent.trim() : null,
                    'Prediction Percentage': predictionText.split(' ')[0], // Assuming percentage is the first part of the text
                    'Evergreen Nerd Narrative': evergreen
                };
            }
        }).filter(item => item !== undefined); // Filter out undefined items
    """, BASE_URL)
    
    driver.quit()  # Don't forget to close the driver

    if not question_cards:
        print("No posts were found on the page.")
        return []
    
    print(f"Found {len(question_cards)} question cards on the page.")

    for card in question_cards:
        print(f"URL: {card['Url']}, Narrative: {card['Narrative']}, Prediction Percentage: {card['Prediction Percentage']}, Evergreen Nerd Narrative: {card['Evergreen Nerd Narrative']}")

    return question_cards

# Scrape the relevant cards
relevant_cards = get_relevant_cards(URL, SCORE_THRESHOLD)

# Create a DataFrame for new data
df_new = pd.DataFrame(relevant_cards)

column_order = ['Url', 'Narrative', 'Prediction Percentage', 'Evergreen Nerd Narrative']
df_combined = None  # Initialize df_combined as None

# Check if the file exists
if os.path.isfile(excel_file):
    df_existing = pd.read_excel(excel_file)
    initial_row_count = len(df_existing)
    
    # Check if all the new data is already in the existing data
    if df_new['Url'].isin(df_existing['Url']).all():
        print("No new unique data to add. The sheet was not changed.")
    else:
        # Merge new data with existing, avoiding duplicates based on the 'Url'
        df_combined = pd.concat([df_existing, df_new])
        before_dropping = len(df_combined)
        df_combined.drop_duplicates(subset='Url', inplace=True, keep='first')
        
        # Reorder the columns in df_combined
        df_combined = df_combined[column_order]
        
        # Calculate how many new rows were added
        new_rows_added = len(df_combined) - initial_row_count
        
        # Check if any rows were dropped
        if len(df_combined) < before_dropping:
            print(f"Sheet updated. Duplicates based on 'Url' were removed. New rows added: {new_rows_added}")
        else:
            print(f"Sheet updated. No duplicates found. New rows added: {new_rows_added}")
else:
    df_combined = df_new[column_order]  # Use the correct syntax here
    new_rows_added = len(df_combined)
    print(f"New file created. Rows added: {new_rows_added}")

# Only write to Excel if df_combined is not None
if df_combined is not None:
    df_combined.to_excel(excel_file, index=False, sheet_name='Predictions')
    print(f"Data written to {excel_file} successfully!")
else:
    print("No changes were made to the Excel file.")