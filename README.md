# 🛍️ Daraz Product Scraper Tool 🤖

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Actions](https://img.shields.io/badge/Automated%20by-GitHub%20Actions-blue?logo=githubactions)](https://github.com/features/actions)

Welcome! This is an automated web scraper that finds product data on **Daraz Bangladesh** 🇧🇩 and sends it to your web application.

It's designed to be a **"set-it-and-forget-it"** tool. 😴 You can host it for **FREE** on GitHub, where it will run on a schedule, collect new product information, and send it directly to your own Google Sheet!

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
-   **Data Receiver:** Google Apps Script

---

## 🚀 Getting Started Guide

To get this scraper working, you need two parts: **Part A** is setting up the Google Sheet to receive the data, and **Part B** is setting up the GitHub Scraper to send the data.

### **Part A: Setting Up the Google Sheet Data Receiver 📝**

First, we need to create a special web app URL using Google Sheets that can listen for data from our scraper.

1.  **Create a New Google Sheet**
    -   Go to [sheets.google.com](https://sheets.google.com) and create a **Blank** spreadsheet.
    -   Name it whatever you like (e.g., "Daraz Scraper Data").
    -   **CRITICAL:** Rename the tab at the bottom from "Sheet1" to **`Products`**. The script needs this exact name to work.

2.  **Open the Apps Script Editor**
    -   In the menu, go to **Extensions** > **Apps Script**. A new tab will open.

3.  **Paste the Script Code**
    -   Delete any placeholder code in the `Code.gs` window.
    -   Copy and paste the entire JavaScript code block below:
    ```javascript
    // This function runs when your Python script SENDS data (POST request)
    function doPost(e) {
      try {
        var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Products");
        
        // Header row with Image URL columns
        if (sheet.getLastRow() === 0) {
          var headers = [
            'Timestamp', 'Product Title', 'Price', 'Discount', 'Product URL',
            'Image URL 1', 'Image URL 2', 'Image URL 3', 'Image URL 4',
            'Image URL 5', 'Image URL 6'
          ];
          sheet.appendRow(headers);
        }

        var productData = JSON.parse(e.postData.contents);
        
        // Handle any number of images, filling up to 6 columns
        var images = productData.image_urls || []; 
        var imageCols = [];
        for (var i = 0; i < 6; i++) {
          imageCols.push(images[i] || ""); // Add the URL or an empty string
        }
        
        var newRow = [
          new Date(), productData.title, productData.price,
          productData.discount, productData.product_url
        ].concat(imageCols);
        
        sheet.appendRow(newRow);
        return ContentService.createTextOutput(JSON.stringify({ "status": "success", "product": productData.title })).setMimeType(ContentService.MimeType.JSON);
      } catch (error) {
        return ContentService.createTextOutput(JSON.stringify({ "status": "error", "message": error.message })).setMimeType(ContentService.MimeType.JSON);
      }
    }

    // This function runs to check for duplicate products
    function doGet(e) {
      try {
        var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Products");
        if (sheet.getLastRow() < 2) {
          return ContentService.createTextOutput(JSON.stringify({ "titles": [], "urls": [] })).setMimeType(ContentService.MimeType.JSON);
        }
        var range = sheet.getRange(2, 2, sheet.getLastRow() - 1, 4); 
        var values = range.getValues();
        var titles = [], urls = [];
        for (var i = 0; i < values.length; i++) {
          titles.push(values[i]);
          urls.push(values[i]);
        }
        return ContentService.createTextOutput(JSON.stringify({ "titles": titles, "urls": urls })).setMimeType(ContentService.MimeType.JSON);
      } catch (error) {
         return ContentService.createTextOutput(JSON.stringify({ "status": "error", "message": error.message })).setMimeType(ContentService.MimeType.JSON);
      }
    }
    ```
    - Click the **Save project** 💾 icon.

4.  **🚀 Deploy the Script as a Web App**
    -   Click the blue **Deploy** button > **New deployment**.
    -   Click the Gear Icon ⚙️ and select **Web app**.
    -   For **Who has access**, change it to **Anyone**. This is required for GitHub to be able to send it data.
    -   Click **Deploy**.

5.  **✅ Authorize the Script**
    -   A popup will ask for permission. Click **Authorize access**.
    -   Choose your Google account.
    -   You will see a "Google hasn't verified this app" warning. This is normal. Click **Advanced**, then click **"Go to ... (unsafe)"**.
    -   Click **Allow**.

6.  **🔗 Get Your Web App URL**
    -   A final popup will show your **Web app URL**.
    -   **COPY THIS URL!** This is the magic link you'll need for the next part. Keep it safe.

### **Part B: Setting Up the GitHub Scraper ☁️**

Now we will set up the GitHub repository to do the scraping and send data to the URL you just created.

1.  **Fork this Repository**
    -   If you haven't already, click the **"Fork"** button at the top-right of this page.

2.  **Add your Web App URL Secret**
    -   In your forked repository, go to **Settings** > **Secrets and variables** > **Actions**.
    -   Click **New repository secret**.
    -   **Name:** `WEB_APP_URL`
    -   **Value:** Paste the **Web app URL** you copied from Google Apps Script in the previous section.

3.  **Enable and Run the Automation!**
    -   Go to the **Actions** tab. Click `I understand my workflows, go ahead and enable them`.
    -   The scraper will now run on its schedule. To run it immediately, click **"Run My Scraper"** on the left and then **"Run workflow"**. Check your Google Sheet in a few minutes! ✨

---

## Running Locally on Your PC 💻

If you prefer to run the scraper on your own computer instead of automatically on GitHub, you can follow these steps after completing Part A.

1.  **Clone the Repo:** `git clone https://github.com/YOUR_USERNAME/Daraz-Product-Scraper-Tool.git`
2.  **Navigate into it:** `cd Daraz-Product-Scraper-Tool`
3.  **Setup Environment:** `python -m venv venv` then `.\venv\Scripts\activate` (for Windows).
4.  **Install packages:** `pip install -r requirements.txt`
5.  **Install browser:** `playwright install --with-deps chromium`
6.  **Set Environment Variable (Windows):** `set WEB_APP_URL="YOUR_WEB_APP_URL_HERE"`
7.  **Run!** `python src/scraper.py`

## 🔧 Customization

You can easily change what the scraper looks for! Open the `src/scraper.py` file and edit the list called `SEARCH_URLS` at the top. Add or remove any Daraz search URLs you want.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.