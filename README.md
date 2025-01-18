# Youbike_data_py
**Python 程式設計與網路資料蒐集期末**

The project is to analyze the traffic flow between YouBike stations in the NTU campus. 
Our team used MariaDB for data storage and Python for YouBike data web scraping and analysis.

Our project begins by using libraries such as requests to download real-time JSON files from the government open data platform. Next, two weeks’ worth of station data is scraped and imported into an SQLite database for storage and management. The necessary data is then extracted from the database and visualized using matplotlib to present key insights. Finally, an analysis is conducted to identify the peak hours for bike rentals and returns at stations both inside and outside the campus.


**The libraries we used for web scraping**
<ul>requests</ul>
<ul>time</ul>
<ul>os</ul>
<ul>xlsxwriter</ul>
<ul>json</ul>
<ul>logging</ul>

**The libraries we used for data analyze/viz**
<ul>logging</ul>
<ul>os</ul>
<ul>sqlite3</ul>
<ul>matplotlib</ul>
<ul>numpy</ul>
