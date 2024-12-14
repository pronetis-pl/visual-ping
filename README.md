# Visual Ping - Monitor Website Changes

Visual Ping is a project that enables monitoring visual changes on websites. The script captures website screenshots, compares them with previous versions, highlights the differences in red, and sends an email with an attachment when changes are detected.

## Features
- Captures website screenshots using Selenium.
- Compares images using the PIL (Python Imaging Library).
- Highlights visual differences in red.
- Sends emails with the differences attached.

---

## Requirements

1. Python 3.8 or newer.
2. Installed dependencies:
    - `selenium`
    - `pillow`
    - `smtplib`
3. ChromeDriver compatible with your Google Chrome version.
4. Access to an SMTP server (e.g., `web9.aftermarket.hosting`).

---

## Installation

1. **Clone the project repository:**
   ```bash
   git clone git@github.com:pronetis-pl/visual-ping.git
   cd visual-ping
