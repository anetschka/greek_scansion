# Performance evaluation

The scripts in this folder can be used for performance evaluations by means of accuracy, precision, recall, and f measure:

* `syllab_eval.py` evaluates the accuracy of the syllabification by comparing your results against a gold standard file. The script expects tab-separated input files and is called like so (check the inline comments for more details):

`python syllab_eval.py <your annotation output file> <syllabification gold standard file> <log file>`

* `scansion_eval.py` calculates precision, recall, and f measure for your scansion annotation. Input files must again be tab-separated. Usage:

`python scansion_eval.py <your annotation output file> <scansion annotation gold standard file> <log file>`