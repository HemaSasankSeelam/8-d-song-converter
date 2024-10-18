import requests
from pathlib import Path
from tqdm.auto import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from webdriver_manager.chrome import ChromeDriverManager
import time

url = "https://audioalter.com/autopanner"

input_path = ""
output_path = ""

songs_path = [i for i in Path(input_path).glob(pattern="*.mp3")]
save_song_folder = Path(output_path)

chrome_service = Service(executable_path=ChromeDriverManager().install())

chrome_options = webdriver.ChromeOptions()
chrome_options.add_extension(extension="") # add the extension path here for blocking adds

driver = webdriver.Chrome(service=chrome_service,options=chrome_options)

wait = WebDriverWait(driver=driver,timeout=20)
driver.get(url=url)

main_window_handle = driver.current_window_handle

pbar = tqdm(total=len(songs_path),colour='green')

for song in songs_path:
    
    pbar.set_description(desc=f"{song}")

    song_browser = driver.find_element(by=By.XPATH,value="//input[@type='file']")
    song_browser.send_keys(song.as_posix())

    sub = wait.until(method=EC.presence_of_element_located((By.XPATH,"//button[normalize-space()='Submit']")))
    sub.submit()

    another_file_button = wait.until(method=EC.presence_of_element_located((By.XPATH,"//button[normalize-space()='Edit another file']")))
    
    driver.implicitly_wait(time_to_wait=7)
     
    anchor_tag = driver.find_element(by=By.XPATH,value="//ul[@role='list']/li//a")
    song_url = anchor_tag.get_attribute(name="href")

    new_song_name = f"{song.stem} 8d" + f"{song.suffix}"
    new_song_path = save_song_folder / Path(new_song_name)

    try:
        response = requests.get(url=song_url)

        if response.status_code == 200:
            with open(new_song_path,'wb') as f:
                f.write(response.content)
        else:
            raise requests.ConnectionError
        
    except Exception as e:
        print(f"Exception occur {e} for the file {song}")
    
    if len(driver.window_handles) > 1: # if any tab opens focus on that tab and closes that tab
        driver.switch_to.window(window_name=driver.window_handles[-1])
        driver.close()

    driver.switch_to.window(window_name=main_window_handle) # switching to main window

    pbar.update(1)
    another_file_button.click()
    time.sleep(2)


pbar.close()

time.sleep(15)
driver.quit()
