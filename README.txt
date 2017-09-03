=====================================================================================
README file for the Text Classification Tutorial
=====================================================================================

This README file is part of the supplemental material published for the paper "Supervised Text Classification: A Tutorial on Model Selection and Evaluation". 
The supplemental material consists of three files:
- README.txt (this file): Contains information on the software, packages and libraries required to run the Python scripts
- TextClassifier.py: Main Python script that is run to develop a new text classifier
- CustomTokenizer.py: Tokenizer imported in the main script 

This README file contains download/installation instructions for the libraries and packages (e.g. NLTK, ScikitLearn, NumPy) required to run the Python scripts. The scripts are written in Python 3.5.2 and can be used on a Windows machine, the installation instructions below are written for Windows 10.


Before you start:
Save both Python scripts in the same folder. In this folder a new subfolder named "output" will be created when running the script, in which the output file(s) will be saved. Your input dataset can be saved in another convenient folder.


Requirements input data:
Make sure your input data is in the right format. The input text documents should be UTF-8 encoded text files (.txt). ScikitLearn requires the dataset in one folder with the text files of the different categories in subfolders. So the folder structure should look like  this:
	Dataset_mainfolder/
		Category_1_subfolder/
			file_1.txt file_2.txt ... file_100.txt
		Category_2_subfolder/
			file_101.txt file_102.txt ... file_200.txt
		Category_3_subfolder/
			file_201.txt ...


Install required packages:
To easily install Python and the required packages/libraries we recommend using Anaconda, a free and easy to use package manager with a large collection of open source packages and community support. --> http://conda.pydata.org/docs/get-started.html


Check if your downloads were successful:
Open the Command Prompt on your computer by typing 'cmd' in your Start menu.
Type 'python -V' and hit enter to check the Python and Anaconda version installed. Something like "Python 3.5.2 :: Anaconda 4.2.0 (64-bit)" should appear, which means the installation was succesful.


Run the Python interpreter:
Type "python" in Command Line and hit enter. The following message should appear, indicating that you are now working in the Python environment: 
"Python 3.5.2 |Anaconda 2.4.1 (64-bit)| (default, Jul  5 2016, 11:41:13) [MSC v.1900 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information."
Leave the interpreter open, you need this to install the required NLTK data and corpora.


Install required NLTK data and corpora:
Certain data and corpora (e.g. stop word lists and stemmers in different languages) need to be downloaded. To do this, follow the installation instructions for the interactive installer on the NLTK website and download all packages. --> http://www.nltk.org/data.html


Open Python script:
You can open the Python script in notepad. We recommend to download Notepad++ because this has code highlighting, which makes the script easier to read. --> https://notepad-plus-plus.org/
Here you can adjust e.g. the path to your dataset (note that forward slashes are used in the path instead of the backslahes used by Windows!), language variables, and the parameter settings.


Run Python script in cmd:
When you have defined the path to your dataset and the parameters, you can save the script and run the script in the Python interpreter in Command Line. To open the command window on the location of the Python script, open the folder where the Python script is saved, make sure no files are selected, and press shift+right mouse click within the folder. Then click on "Open command window here". Type "python TextClassifier.py" and hit enter, the script will start. 

Beware, depending on the number and length of the text documents in the dataset and the defined parameter grid, it can take up to several hours to run the complete script. We therefore advise to first run the script on a small subset of your dataset (e.g. 30 texts per class) or a subset of parameters (e.g. reduce the number of different parameter values to be compared) to check whether the script runs correctly. 


Current settings:
The script is currently set to run three categories (Atheism, Graphics, and Religion) from the English "20 Newsgroups" data set, using the validation strategy, parameter grid, and weighted performance scores for the multiclass classifier as defined in the paper. When applying the script to your own data set, make sure that: 
- you defined the language of the text documents
- you defined the path to the data set on your computer (using forward slashes)
- your data set is organized using the described folder structure
- the text files are in the required format (one UTF-8 encoded .txt file per document)
- you use the binary performance scores for the binary model, and multiclass performance scores (micro-, macro-, or weighted-average) for the multiclass model


Output file:
The output file is organized as follows:
- Print of defined parameter grid for GridSearchCV
- Print best score + best parameter set
- K-fold CV grid scores for every parameter combination
- Performance scores selected model on test set
- Top X most informative features
- Confusion matrix final model


More information:
- Python: https://www.python.org/
- ScikitLearn documentation: http://scikit-learn.org/stable/documentation.html
- NLTK documentation: http://www.nltk.org/
- NumPy: http://www.numpy.org/