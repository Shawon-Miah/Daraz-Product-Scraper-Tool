# 🛍️ Daraz Product Scraper Tool 🤖

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Actions](https://img.shields.io/badge/Automated%20by-GitHub%20Actions-blue?logo=githubactions)](https://github.com/features/actions)

Welcome! This is an automated web scraper that finds product data on **Daraz Bangladesh** 🇧🇩 and sends it to your web application.

It's designed to be a **"set-it-and-forget-it"** tool. 😴 You can host it for **FREE** on GitHub, where it will run on a schedule, collect new product information, and send it wherever you want!

## ✨ Key Features

-   ✅ **Fully Automated:** Runs on a schedule using GitHub Actions. No need to run it manually!
-   🔎 **Smart Scraping:** Checks for products you've already saved and only scrapes new ones.
-   🖼️ **Robust Image Handling:** A powerful 3-step validation process ensures you only get valid, high-quality product images.
-   🔧 **Easily Configurable:** You can easily change what to search for, how many products to scrape, and more.
-   💖 **Beginner Friendly:** Designed to be forked and used with very simple setup steps.

## 🛠️ Technology Stack

-   **Language:** Python 🐍
-   **Scraping Libs:** Playwright & BeautifulSoup4
-   **Automation:** GitHub Actions 🚀
-   **Data Sending:** Requests

---

## 🚀 Getting Started

You have two amazing options to use this scraper. The GitHub method is recommended for easy, automated, and free hosting.

### **Method 1: Run on GitHub (Recommended & Automated) ☁️**

This is the easiest way. It's fully automated and completely free.

#### **Step 1: Fork this Repository**
Click the **"Fork"** button at the top-right of this page. This will create a complete copy of this project in your own GitHub account.

#### **Step 2: Add your Web App URL Secret**
The scraper needs to know *where* to send the data it collects. You must provide this URL as a "secret" so it stays private.

1.  In your new forked repository, go to **Settings** > **Secrets and variables** > **Actions**.
2.  Click the **New repository secret** button.
3.  **Name:** `WEB_APP_URL` (It must be exactly this!)
4.  **Value / Secret:** Paste the URL of your web app (for example, a Google Apps Script `doPost` URL that adds data to a Google Sheet).
5.  Click **Add secret**.

> **⚠️ VERY IMPORTANT:** The scraper will not work without this secret! It is designed to check for it and will stop if it's not found.

#### **Step 3: Enable and Run the Automation!**
1.  Go to the **Actions** tab in your repository.
2.  If you see a button that says `I understand my workflows, go ahead and enable them`, click it.
3.  That's it! The scraper will now run automatically on the schedule (currently every 20 mins between certain hours).
4.  To run it immediately, click **"Run My Scraper"** on the left, then the **"Run workflow"** button.

### **Method 2: Run on Your Local PC 💻**

If you want to run the scraper on your own computer, follow these steps.

#### **Step 1: Clone the Repository**
```bash
git clone https://github.com/Shawon-Miah/Daraz-Product-Scraper-Tool.git
cd Daraz-Product-Scraper-Tool
```

#### **Step 2: Create a Virtual Environment (Highly Recommended)**
This keeps your project's dependencies separate.
```bash
# For Windows
python -m venv venv
.\venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### **Step 3: Install All the Requirements**
```bash
pip install -r requirements.txt
```

#### **Step 4: Install the Necessary Browser for Playwright**
```bash
playwright install --with-deps chromium
```

#### **Step 5: Set the Environment Variable**
This is the local version of adding a GitHub Secret.

-   **On Windows (Command Prompt):**
    ```cmd
    set WEB_APP_URL="YOUR_WEB_APP_URL_HERE"
    ```
-   **On macOS/Linux (Terminal):**
    ```bash
    export WEB_APP_URL="YOUR_WEB_APP_URL_HERE"
    ```
*(Replace `"YOUR_WEB_APP_URL_HERE"` with your actual URL)*

#### **Step 6: Run the Scraper!**
```bash
python src/scraper.py
```
You should now see the scraper starting in your terminal! 🎉

---

## 🔧 Customization

Want to scrape for different things? It's easy! Open the `src/scraper.py` file and edit the configuration variables at the top:

-   `TARGET_PRODUCTS_PER_RUN`: How many new products to find each time.
-   `MAX_PAGES_TO_CHECK`: How many search pages to look through.
-   `SEARCH_URLS`: A big list of all the Daraz search queries. **Add, remove, or change these URLs to whatever you want!**

## 📄 License

This project is licensed under the MIT License. Feel free to use and modify it! See the [LICENSE](LICENSE) file for more details.