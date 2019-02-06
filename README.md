# voobly-parse-aoe2-game-data
This is a python file for users to access the voobly website, and visit each player in the ranking, and each history game they have played. 

Here is the example of the raw data from: https://www.voobly.com/match/view/19235723
![screen shot 2019-02-05 at 11 21 36 pm](https://user-images.githubusercontent.com/33019130/52320349-de234080-299c-11e9-9d6f-23b2ae206af4.png)



# Data Format
The data is stored in MongoDB which would be the best storage method (key-value database)for this data.

The data is formatted as a tree structure:
  Match Detail -> Win/Lose Team -> Overall Score/Military/... -> Units Killed/Units Lost/...

# Module
The module you have to have are:

* BeautifulSoup4
* pymongo
* requests
* pandas
