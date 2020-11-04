# wiki_search_engine
wikipedia search engine

Sample files :
https://drive.google.com/drive/folders/1gsfHWcmdHu4mQ7SxZYK3hpI-AkTfpbHx?usp=sharing


wikipidea dump file link :
https://dumps.wikimedia.org/enwiki/latest/


It is a search engine based on k-way merge sort based indexing and further uses relevance ranking using tf-idf scores.

<h2> Challenges </h2>
  -> Difficult to process such huge Data dump of 73 GB
  -> Can not store word & its posting list into a main memory, So Used K-way Merge sort
  -> Can not Load full final index into main memory, So Bild Secondary Index on top of Primary Index (Posting List)

<h3> phase 1 </h3>
  -> Used title, infobox and category to build indexes.
  -> returning the title of the wikipedia page.
  
 <h3> TODO : phase 2 </h3>
    -> Use body(text) of the wikipedia pages as well to increase relevancy.
    -> return the URLs of the wikipedia pages instead of titles


<h3> phase 1 sample result </h3>

![wikiss](https://user-images.githubusercontent.com/41481020/98165332-b5323580-1f0b-11eb-9b3b-215699bb8e63.png)

