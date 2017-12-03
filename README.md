## Search amazon.com
Keyword tracker requirements:
Input file (which the scraper uses)  - input.csv
Column 1 is the ASIN of the product I want to measure the rank of for a given keyword
Column 2 is the search term used to execute the search
Column 3: active (yes/no) – if set to “no”, then the scraper ignores this keyword
1 ASIN can map to one or more keywords
Should be a file that I can edit and save
App then uses input source to drive scraping of Amazon US site (amazon.com).
App enters keyword (search term) in amazon search box, executes search and then looks for the associated ASIN in the search results
The app may need to click to subsequent pages on Amazon.com to see the next page of search results (assuming ASIN is not found on 1st page)
When the search term-ASIN match is found, the app records the search term position of the ASIN.
For example, if the ASIN was the 8th listing, the App would record “8” next to that ASIN/search-term pair
Advertisement listings (usually there are at least 2 per page) should not be included in the matching or the counting (so, treat them as if they don’t exist)
Output file fields:
Column A: ASIN
Column B: SEARCH TERM
Column C: DATE
Column D: PAGE NUMBER
Column E: recorded rank (or “NF[x]”) or “Failed” (in the case of crawler error)
If a search term has been set to inactive, then the cell can just record “inactive”
