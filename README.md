# Autocomplete API Data Extraction

## Problem Statement

An autocomplete API running at `http://35.200.185.69:8000`. The task is to extract **all possible names** available through this API's autocomplete system. However, there is no official documentation, so the API must be explored systematically to understand its behavior, limitations, and constraints.

## Project Overview

This project aims to **efficiently** extract and document all possible names from the API. The process includes:

- Discovering how the API works through **exploration and testing**
- Handling **rate limiting and retries** to ensure smooth data extraction
- Implementing an optimized **breadth-first search (BFS)** approach to query the API efficiently
- Logging and analyzing API behavior for **different versions (`v1`, `v2`, `v3`)**

## API Exploration & Key Findings

During API testing, the following key insights were discovered:

1. **API Endpoint Structure**:
   - The known endpoint: `/v1/autocomplete?query=<string>&page=<int>`
   - Multiple versions exist: `/v2/autocomplete`, `/v3/autocomplete`

2. **Pagination**:
   - The API returns results in pages
   - The parameter `page` is required to navigate multiple pages

3. **Rate Limiting**:
   - The API enforces rate limiting, occasionally returning **HTTP 429 (Too Many Requests)**
   - Implemented a **backoff strategy** to retry requests after an increasing delay

4. **Search Behavior**:
   - Searching with a **single character (`a`, `b`, `c`, etc.)** returns names starting with that letter
   - Extending queries (`ap`, `app`, `appl`) helps discover more names

5. **Data Format**:
   - The API response contains a **`results` list** with names
   - A **`has_next_page`** field indicates whether there are more results for pagination

## Approach & Implementation

### 1. **Breadth-First Search (BFS) for Query Expansion**
Instead of blindly making all possible queries, a **queue-based BFS approach** is used:
- Start with single-character prefixes: `a` to `z`
- For each prefix, query the API and extract names
- If a name is found that extends the current prefix, generate a new query by appending the next letter
- Avoid duplicate queries using a **set to track processed prefixes**

### 2. **Rate Limiting & Error Handling**
- Implemented **automatic retries** for HTTP errors (429, 500, 502, etc.)
- Used **exponential backoff** when the API returns a `429 Too Many Requests` error
- Added a **delay mechanism** to avoid hitting the rate limit too quickly

### 3. **Multi-Version Handling**
- The script runs for **three API versions**: `v1`, `v2`, and `v3`
- Stores results in separate files (`names_v1.txt`, `names_v2.txt`, `names_v3.txt`)
- Logs the total number of **requests made and results collected**

## Code Structure
```
autocomplete_api_scraper/      # Parent directory
│── src/                       # Source code folder
│   ├── __init__.py            # Marks 'src' as a package
│   ├── autocomplete_scraper.py # Main script for API interaction
│
│── README.md                   # Project documentation
│── requirements.txt             # Dependencies
│── example_output.txt           # Sample output of extracted names
│── api_client.log               # Log file for API requests/errors
│── venv/                        # Virtual environment (optional)
```

## Installation & Setup

### **Clone the Repository**
```
git clone https://github.com/Dronesh77/autocomplete_api_scraper.git
cd autocomplete_api_scraper
```
### **Setup Virtual Environment (Optional)**
```
python -m venv venv
source venv/bin/activate  # On Mac/Linux
venv\Scripts\activate     # On Windows
```
### **Install Dependencies**
`pip install -r requirements.txt
`
### **Run the Script**

`python src/autocomplete_scraper.py`
`

### **Prerequisites**
- Python 3.x

## **Output**
- Extracted names will be stored in `example_output.txt`

- Log details will be available in `api_client.log`



## **Future Enhancements**
- Optimize multi-threading for faster execution

- Implement graph-based query expansion for better coverage

- Create a dashboard to visualize extracted names