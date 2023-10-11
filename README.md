# ted-europa-data-scrapper

## Summary:

Allows you to bulk scrape the <u>DATA</u> pages from documents from [Ted EUROPA](https://ted.europa.eu/).

## Features:

* Allows you to scrape data from start to finish;
* Saves a state if you don't want to scrape the data all at once;
* Allows you to update your data with the newest one;

## Tools:

* Language: Python
* Libraries: BeautifulSoup4

## Run Locally

1. Clone the project:

```bash
  git clone git@github.com:dandr94/ted-europa-scrap.git
```

2. Go to the project directory:

```bash
  cd ted-europa-scrap/
```

3. Install virtual environment:

```bash
  python -m venv /venv
```

4. Activate virtual environment:<br>

- Windows CMD:

```bash
  .\venv\Scripts\activate.bat
```

- Windows Powershell:

```bash
  .\venv\Scripts\Activate.ps1
```

- Linux:

```bash
  source /venv/bin/activate
```

5. Create a `.env` and add the following environment variables to your `.env`:</br>
   ```JSESSIONID=your_jsessionid_here```</br>
   ```LG_PREF=en``` (breaks the app if not in en language otherwise)</br>
   ```CCK1=your_cck1_here```</br>
   _to see these settings go to [ted-europa](https://ted.europa.eu/) and go to developer mode(F12):_

- Chrome: click on tab 'Application', then on the left side click 'Cookies' and click on the cookie. You will see the values
  on your right, click on them and copy them to your .env
- Firefox: click on tab 'Storage', then on the left side click 'Cookies' and click on the cookie. You will see the values on
  your right, click on them and copy them to your .env

6. Install dependencies:

```bash
  pip install -r requirements.txt
```

7. Run the program:

```bash
  python main.py
```

## DATA
The program saves the data in a JSON format and follows this structure:
```json
[
  {
    "URL": "...",
    "Title": "...",
    "Notice publication number": "...",
    "Publication date": "...",
    "OJ S issue number": "...",
    "Town/city of the buyer": "...",
    "Official name of the buyer": "...",
    "Original language": "...",
    "Country of the buyer": "...",
    "Type of buyer": "...",
    "EU institution/agency": "...",
    "Document sent": "...",
    "Type of contract": "...",
    "Type of procedure": "...",
    "Notice type": "...",
    "Regulation": "...",
    "Type of bid": "...",
    "Award criteria": "...",
    "Common procurement vocabulary (CPV)": "...",
    "Place of performance (NUTS)": "...",
    "Internet address (URL)": "...",
    "Legal basis": "..."
  }
]
```
- You can download my scrapped data for all Active notices and result of the Business opportunities from 6.10.2023 to the end of the search results from [HERE](https://www.dropbox.com/scl/fi/732w88tyo0au69qxceeg0/output.json?rlkey=mqzpysrpijkf3n4yikei8nqxn&dl=0). File size: 109 MB. Lines: 2,067,382 

## Problems
Here are some problems that you can experience:
- For some reason I can't make it to fetch cookies dynamically, so you need to manually put the needed cookies to be able to fetch the data, otherwise the server will not allow you. `requests.Session()` makes a session and returns the right cookies automatically but for some reason the server does not allow these cookies. Maybe I'm missing something, but I didn't find a solution for this problem. So if you don't fetch all the data at once you will have to update your .env with the new data when you start to scrape again, because the session will expire, and you need a new JSESSIONID token.
- Sometimes the server returns an error if you don't go manually to the search results. For example: you go to the website main page, copy the needed data, start app -> app returns an error because the server refuses your request. For some reason you need to go manually to the Advance search and click Search then it will work... Why? Who knows....