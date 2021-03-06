## Search amazon.com
Keyword tracker requirements:

Input file (which the scraper uses)  - input.csv

* Column 1 is the ASIN of the product I want to measure the rank of for a given keyword
* Column 2 is the search term used to execute the search
* Column 3: active (yes/no) – if set to “no”, then the scraper ignores this keyword

App then uses input source to drive scraping of Amazon US site (amazon.com).
App enters keyword (search term) in amazon search box, executes search and then looks for the associated ASIN in the search results
The app may need to click to subsequent pages on Amazon.com to see the next page of search results (assuming ASIN is not found on 1st page)
When the search term-ASIN match is found, the app records the search term position of the ASIN.
For example, if the ASIN was the 8th listing, the App would record “8” next to that ASIN/search-term pair
Advertisement listings (usually there are at least 2 per page) should not be included in the matching or the counting (so, treat them as if they don’t exist)

Output file fields:
* Column A: ASIN
* Column B: SEARCH TERM
* Column C: DATE
* Column D: PAGE NUMBER
* Column E: recorded rank (or “NF[x]”) or “Failed” (in the case of crawler error)
* If a search term has been set to inactive, then the cell can just record “inactive”

## Set as a cron job (daily)
* open terminal ```cd``` to amazon-search and grab the path with ```pwd``` e.g. /Users/xxxx/amazon-search
* exec ```crontab -e``` and add the following

```
* 07 * * * cd /Users/xxxx/amazon-search && source ./path.sh && python run.py
```

so it will execute at 7:00 AM
reference: [cron job](https://ole.michelsen.dk/blog/schedule-jobs-with-crontab-on-mac-osx.html)
* save it
* exec ```crontab -l``` to make sure the job is added
* after it's run, you can run again ```crontab -l``` to check if it's successful
e.g. You have new mail in /var/mail/rafalfusik so you can ```vi /var/mail/rafalfusik```


### Reviews
* add a new url to scrape reviews from
```bash
https://www.amazon.com/BRIXTON-Mens-Brood-Newsboy-Snap/product-reviews/B0812755NJ/ref=cm_cr_arp_d_viewopt_srt?ie=UTF8&reviewerType=all_reviews&sortBy=recent&pageNumber=1,yes
```
one must add it to `reviews_input.csv` and set `yes/no` to `yes`, `no` means that it'll be ignored
* output file: `reviews_output.csv`
* reviews settings:
```bash
reviews:
  input_file: reviews_input.csv
  output_file: reviews_output.csv
  pages: 200
```
where:
pages - max. number of pages to scrape reviews from for each given url

##### Run reviews script
```bash
python reviews.py
```

### ETSY Reviews
* add a new url to scrape reviews from
```bash
https://www.etsy.com/shop/AmeriTrendsCo/reviews?ref=l2-see-more-feedback,yes
```
one must add it to `reviews_etsy_input.csv` and set `yes/no` to `yes`, `no` means that it'll be ignored
* output file: `reviews_etsy_output.csv`
* reviews settings:
```bash
reviews_etsy:
  input_file: reviews_etsy_input.csv
  output_file: reviews_etsy_output.csv
  pages: 10
  split: "on"  # english: "on", polish: "w dniu"
  all_data: true
```
where:
* `pages` - max. number of pages to scrape reviews from for each given url
* `all_data` - set to `true` if you wish to scrap a user nick and comment as well

##### Run reviews script
```bash
python reviews_etsy.py
```

### Search ASINS 

1. Run script which collects ASINs from 1 to x pages deep
2. Ability to apply filters to the collection process:
* Filter out ASINs associated with ads
* Filter out ASINs that don’t contain a specific (case-insensitive) word in the title. For example, I may require that each ASIN has the word “Dungeon” in the title.
* Filter out ASINs that DO contain specific case-insensitive words. For example, I may want to exclude listings with the word “Disney” in the title.
* The keyword conditions can be OR conditions (for example, filter out ASINs that contain either “Disney” or “Nike”). For now, I don’t think I need AND condition.
3. Output to a CSV - ASIN and the corresponding title

##### Run reviews script
```bash
python search.py
```

##### Files
* search.py
* search_in.csv
* search_out.csv
