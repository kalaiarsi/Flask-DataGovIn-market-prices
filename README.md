# Flask-DataGovIn-market-prices
Flask webapp to download market prices from data.gov.in catalog. 

Market Price - Flask webapp: Creates SQL db, scraps data.gov.in for daily market price of the variety in XML file, extracts data, pushed it to db. (no job queue done. so visible delay on 127.0.0.1:5000 while scraping + extracting data). uses selenium
