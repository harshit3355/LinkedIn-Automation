# LinkedIn Connection Request Automation

A Selenium script that logs into LinkedIn, searches for people by role, and sends connection requests across the results, paging through until it runs out.

## Why this exists

Sending connection requests one at a time is the slowest part of a job search or a recruiting push — search, click, connect, dismiss the modal, scroll, repeat, several hundred times. This automates that loop with browser automation, driving the real UI in a real Chrome window rather than calling an API.

It is a small, readable example of practical Selenium: waiting for elements properly with `WebDriverWait` instead of sleeping and hoping, handling a search flow that changes the page underneath you, and paging through infinite-scroll results.

## Read this before you run it

**Automated connection requests violate LinkedIn's User Agreement.** LinkedIn actively detects this behaviour, and the consequences escalate from a temporary restriction to permanent account loss. There are also weekly invitation limits that this script does nothing to respect.

Run it against an account you can afford to lose, or treat the repository as a Selenium reference and not something to point at your real profile. That is your call to make — the tooling is here either way.

## How it works

1. `start_browser()` launches Chrome via `webdriver-manager`, which downloads a matching ChromeDriver automatically, and opens the LinkedIn login page.
2. `login_to_linkedin()` fills in the credentials from your `.env` and submits.
3. `send_connection_requests()` searches for the configured role, switches to the **People** tab, and walks the result pages clicking *Connect*.

## Setup

```bash
pip install selenium webdriver-manager dotenvy
```

Fill in `.env` — it ships with placeholder values:

```
EMAIL="your-linkedin-email"
PASSWORD="your-linkedin-password"
```

`.env` is currently tracked by git. Add it to `.gitignore` before you put real credentials in it, or you will commit your password.

## Usage

```bash
python main.py
```

Chrome opens and drives itself. Do not use the window while it runs — stealing focus or clicking breaks the element lookups.

To search for a different role, change the search term in `send_connection_requests()`:

```python
search_box.send_keys("DevOps Engineer")   # change this
```

## Notes and limits

- **It needs a visible browser.** No headless mode; LinkedIn treats headless sessions differently and the flow is easier to debug when you can watch it.
- **The selectors will break.** They depend on LinkedIn's current DOM — class names like `search-global-typeahead__input` and XPath text matches on "People". When LinkedIn ships a UI change, the script stops working and the XPaths need updating. That is inherent to UI automation, not a bug to be fixed once.
- **Two-factor authentication is not handled.** If your account has 2FA enabled, login stops at the challenge.
- **Timing is fixed `sleep()` calls** in places. On a slow connection, raise them.
- **No rate limiting.** The paging loop keeps going. Add a delay and a cap unless you want the account flagged quickly.
