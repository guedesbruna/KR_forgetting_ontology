# kr_project2_forgetting_ontology

This project is based on the forgetting ontology applied into OWL language files in order to evaluate behavior of classes when forgetting different signatures.
It provides an individual class-by-class analysis and a cluestering of both the most densely and sparsed connected classes in the dataset.
The two clusters are then used to show the enhanced pottential of forgetting in the extreme cases of forgetting very common and uncommon subsumptions of the dataset.

## Structure of execution
- common_functions.py
- plots.py

For a better visualization of hierarchies, the tools Protege-5.5.0 and lethe-ui.sh can be used. 

This code requires a Python and a Java installation.
It also requires the download of kr_functions.jar and lethe-standalone.jar, that can be found here: https://github.com/schlobac/kr_project2_explanation_by_forgetting


**ALERT**: time of execution diverges if the forgetting method is applied for highly connected nodes in more than 10 iterations.
