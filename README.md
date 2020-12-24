# Interactive-Knowledge-Graph-for-CaseLaw-Analysis
	*Knowledge graph for law case project - Georgia Tech CSE 6242.
	*We aim to visualize a law case document to improve the reading experience.
	*Contributed by: Zichen Bai, Yun-Hsuan Chen, Tien-Chi Hsin, Ching-Chieh Huang, Ming-Ying Li, and Ting Liao(Listed in alphabetical order)

# INSTALLATION - How to install and setup your code
## Data collection (scrape) part:
### Outline
We scrape the text data from casetext.com with python library BeautifulSoap and selenium. At the beginning we should create an account for casetext.com and use python selenium library to simulate the user’s login. After login, we search for some keywords and copy the URL that show the first page of searching result. (just need to modify little bit of URL, we can traverse every page with the same keyword). With the search result html data, we use a BeautifulSoap object to find the tags that have the hyperlink to the case context. For each link, we use another BeautifulSoap object to find all paragraphs we need. After completing, store the text data in a txt file.  
### Package
- beautifulsoup4==4.9.3
- selenium==3.141.0
- requests==2.24.0


## NLP (Backend) part:

### Outline
#### A. LDA topic clustering in Colab over all files
#### B. Relation extraction for KG over all files
#### C. future deployment to append a single file into processing json file for LDA and KG. (Optional) as it is not main workflow in our project

### Important: Please change file paths for your google drive or local computers in code segments due to saving and writing files

### A. LDA topic clustering in Colab over all files

(1) upload LDA_all.ipynb in NLP directory to your google drive.
(2) upload all legal documents to the same place in a txt format without other txt files.  (we do not offer the files here due to talent issue)


### B. Relation extraction for KG over all files
(1) in your computer, please create a python3.7 environment and install the right version python package in requirement.txt in NLP directory strictly.
   Or, the following packages
   spacy==2.1.0
   networkx==2.5
   matplotlib==3.3.2
   pandas==1.1.3
   neuralcoref==4.0
   --no-binary neuralcoref
(2) install other package you may need if you cannot import python package you need (not strictly for version and please do not change the version for strict ones) 
(3) put all legal documents which are related background part to the same place in a txt format in one directory you wish without other txt files. 
(we do not offer the files here due to talent issue)


### C. Future deployment to append a single file into processing json file for LDA and KG. (Optional) as it is not main workflow in our project
(1) go to future_upload_deployment directory from our github
(2) make sure you put new_file.txt(a single file to be appended), file_topic.json, tokenizer.pkl, tokenizer.pkl, and all_files_triples_sentence.json
(3) install flask, the environments and package from A. and B.


# EXECUTION
## Data collection:
### scrape script (scrape_case_context.py):
this tool is the template to scrape data from target website.
## Font-end:
### LDA tree page (lda_tree.html): 
This page visualizes categories provided by the LDA model as a tree structure in “data/lda_tree_names.json”. To simplify the information, we create an additional layer to include similar cases into a branch. 

### Knowledge graph page (knowledge_graph.html):
This tool extract sentence cropped by the back-end in “data/all_files_triples_sentence.json”. It displays the visualization of the relationships between objects in the law case document. 
* To locate the sentence of a set of nodes: (1) Click blue node (relation node). (2) The sentence will be highlighted in the article. (3) Double click to remove the highlight
* To add a new user-defined “subject-relation-object” nodes: (1) Type in a subject name, relation, and the object name into the input fields at the top-left corner. (2) Click submit to add new nodes into the graph. 
* To add a new sentence-related “subject-relation-object” nodes: (1) Click the sentence. (2) Type in the object, relation, and subject. (3) Click “submit”. (4) Click the blue node will have the same highlight effect
* Filter/Search: (1) Type in object name. (2) Click “Filter Object” (3) Type in new target names if needed. (4) To remove the filtering condition, click the filter tag.

### Welcome page (landing.html):
This page is our welcome page with background animation

### Introduction page (about.html):
This page briefly describe our project

## NLP (Backend) part:

### Outline
#### A. LDA topic clustering in Colab over all files
#### B. Relation extraction for KG over all files
#### C. future deployment to append a single file into processing json file for LDA and KG. (Optional) as it is not main workflow in our project

### Important: Please change file paths for your google drive or local computers in code segments due to saving and writing files


### A. LDA topic clustering in Colab over all files

#### Usage:
(1) Run the code segments sequentially (including installation segments)
(2) please rerun some previous segments if you need to restart variable environments after some package installation
(3) Run code segments until the  one with a comment "# saving"
(4) You get file_topic.json, tokenizer.pkl, and tokenizer.pkl. Good jobs. Please download them into your future_upload_deployment directory from our github.
(4.5) The following steps are performed in your local computer
(5) Copy file_topic.json and rename the copy one into file_topic_1120.json
(6) Run LDA_KG_One2One.py with into file_topic_1120.json and all_files_triples_sentence.json from (2) part to get file_topic_pruning.json 
(7) you can use the one in display/data/expired)
(8) Put file_topic_pruning.json in display and run tree_data.py to obtain file_topic_1120_reverse4.json
(9) Rename file_topic_1120_reverse4.json into lda_tree_names.json

### B. Relation extraction for KG over all files

#### Usage:
(1) put DVA_NLP_law_KG_V3 in NLP directory into the (3) directory you create and then run it about 4-5 hours (This long time is for processing 1000 documents) 
(2) You will obtain all_files_triples_sentence.json for (1), (3), and visualization part

### C. Future deployment to append a single file into processing json file for LDA and KG. (Optional) as it is not main workflow in our project

#### Usage:
(1) run deploy and enter the file name (here is new_file.txt)
(2) You obtain all_files_triples_sentence.json and file_topic.json with the information from new_file.txt
(3) Note this experimental part is for flask and our A. B. combination. It is not included in our main workflow
