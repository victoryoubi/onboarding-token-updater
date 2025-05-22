import time
import gspread
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from oauth2client.service_account import ServiceAccountCredentials

# === 設定 ===
CREDENTIALS_FILE = "credentials.json"  # GitHub Actionsで生成される
SPREADSHEET_NAME = "250522_Onboarding施策分析シート"
WORKSHEET_NAME = "設定"
TOKEN_CELL = "F1"

EMAIL = "b.fujioka@mov.am"
PASSWORD = "Vic18miracle@"


def fetch_token():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1200,800")

    driver = webdriver.Chrome(options=options)

    try:
        print("🔐 トークン取得中...")

        # ログインページへアクセス
        driver.get("https://manage.onboarding-app.io")
        time.sleep(3)

        # ログイン処理
        driver.find_element(By.ID, "email").send_keys(EMAIL)
        driver.find_element(By.ID, "password").send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # ダッシュボードに遷移するまで待機
        WebDriverWait(driver, 15).until(lambda d: "dashboard" in d.current_url)
        print("✅ ログイン成功:", driver.current_url)

        # レポートページへ遷移
        driver.get("https://manage.onboarding-app.io/report?period=last_thirty_days&type=popup")
        time.sleep(3)

        # トークンをlocalStorageから取得（最大10回リトライ）
        token = None
        for _ in range(10):
            token = driver.execute_script("return localStorage.getItem('api_token');")
            if token:
                break
            time.sleep(1)

        if token:
            print("🔑 取得成功: トークン = ", token)
        else:
            print("❌ localStorageにトークンがありません")

        return token

    except Exception as e:
        import traceback
        print("⚠️ エラー発生:")
        traceback.print_exc()
        return None

    finally:
        driver.quit()


def write_token_to_sheets(token):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)

    sheet = client.open(SPREADSHEET_NAME).worksheet(WORKSHEET_NAME)
    sheet.update(range_name=TOKEN_CELL, values=[[token]])  # ← [[]] で2次元リストに
    print(f"✅ トークンを「{WORKSHEET_NAME}!{TOKEN_CELL}」に書き込みました。")


# === 実行ブロック ===
if __name__ == "__main__":
    token = fetch_token()
    if token:
        write_token_to_sheets(token)
        print("✅ トークン取得と書き込み 完了！")
    else:
        print("❌ トークン取得に失敗しました。")

