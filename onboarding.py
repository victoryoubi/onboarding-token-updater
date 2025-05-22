import time
import gspread
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from oauth2client.service_account import ServiceAccountCredentials

# === 設定 ===
CHROMEDRIVER_PATH = "C:/Users/藤岡弥呼太/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe"
CREDENTIALS_FILE = "C:/Users/藤岡弥呼太/Downloads/credentials.json"
SPREADSHEET_NAME = "250522_Onboarding施策分析シート"
WORKSHEET_NAME = "設定"
TOKEN_CELL = "F1"

EMAIL = "b.fujioka@mov.am"
PASSWORD = "Vic18miracle@"


def fetch_token():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1200,800")
    options.add_argument("--headless=new")  # ← ヘッドレスモード
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)

    try:
        # ログインページへアクセス
        driver.get("https://manage.onboarding-app.io")
        time.sleep(3)

        # ログインフォーム入力
        driver.find_element(By.ID, "email").send_keys(EMAIL)
        driver.find_element(By.ID, "password").send_keys(PASSWORD)

        # ログインボタンをクリック
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # /dashboard に遷移するまで待機
        WebDriverWait(driver, 10).until(lambda d: "dashboard" in d.current_url)
        print("✅ ログイン成功:", driver.current_url)

        # レポート画面に遷移
        driver.get("https://manage.onboarding-app.io/report?period=last_thirty_days&type=popup")
        time.sleep(3)

        # トークン取得（最大10回試す）
        token = None
        for _ in range(10):
            token = driver.execute_script("return localStorage.getItem('api_token');")
            if token:
                break
            time.sleep(1)

        if token:
            print("🔑 取得成功: トークン = ", token)
        else:
            print("❌ localStorageからトークンが取得できませんでした")

        return token

    except Exception as e:
        import traceback
        print("⚠️ エラー発生:")
        traceback.print_exc()
        return None

    finally:
        driver.quit()


def write_token_to_sheets(token):
    # Sheets API認証
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)

    sheet = client.open(SPREADSHEET_NAME).worksheet(WORKSHEET_NAME)
    sheet.update(TOKEN_CELL, [[token]])  # ← 修正済み
    print(f"✅ トークンを「{WORKSHEET_NAME}!{TOKEN_CELL}」に書き込みました。")


# === 実行ブロック ===
if __name__ == "__main__":
    print("🔐 トークン取得中...")
    token = fetch_token()
    if token:
        write_token_to_sheets(token)
        print("✅ トークン取得と書き込み 完了！")
    else:
        print("❌ トークン取得に失敗しました。")
