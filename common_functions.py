from numpy import *
from myProgram import *
import os
import subprocess 
import re
import networkx as nx

def extract_subclass():
    subclasses = []
    with open("datasets/subClasses.nt", "r") as sub:
        for line in sub:
            line1 = line.split()
            line2 = line1[0].replace("<", "")
            line3 = line2.replace(">", "")
            if line3 not in subclasses:
                subclasses.append(line3)
    return subclasses     


def extract_subclass_class(): #don't distinguish between class and subclass
    subclasses = []
    with open("datasets/subClasses.nt", "r") as sub:
        for line in sub:
            line1 = line.split()
            line2 = line1[0].replace("<", "")
            line3 = line2.replace(">", "")
            if line3 not in subclasses:
                subclasses.append(line3)
            line2 = line1[2].replace("<", "")
            line3 = line2.replace(">", "")
            if line3 not in subclasses and line3!='script':
                subclasses.append(line3)
    return subclasses
    
    
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

flatten = lambda l: [item for sublist in l for item in sublist]

def get_input_metrics(direct_output):
    s = str(direct_output)
    result = re.search('Input(.*)following', str(direct_output))
    output_clean = result.group(1).split('\\n')
    keys = ['n_axioms', 'av_axiom', 'definers', 'n_restrictions']
    values = flatten([[float(s) for s in output_clean[i].split() if is_number(s)] for i in range(len(output_clean))])
    dict_input = dict(zip(keys,values))
    return dict_input  
    
    
def process_output(direct_output):
    s = str(direct_output)
    result = re.search('forgotten:(.*)nForgetting', s)
    forgotten = [_ for _ in str(result.group(1)).split('\\n') if _ and _!='\\'] 
    output_clean = [x for x in str(direct_output).split('!')[1].split('\\n') if x and x!="'" and x.startswith('Exporting')==False and x.startswith('Finished')==False]
    #further cleaning
    values = [[float(s) for s in output_clean[i].split() if is_number(s)][0] for i in range(len(output_clean))]
    return values        


def main_execution():
    # This is an example puython programme which shows how to use the different stand-alone versions of OWL reasoners and forgetting programme
    #########the input ontology will change will the new file generated in the end of each loop
    # Choose the ontology (in the OWL format) for which you want to explain the entailed subsumption relations.
    inputOntology = "datasets/pizza.owl"

    # Choose the set of subclass for which you want to find an explanation.
    # this file can be generated using the second command (saveAllSubClasses)
    inputSubclassStatements = "datasets/subClasses.nt"

    # Choose the ontology to which you want to apply forgetting. This can be the inputOntology, but in practise
    # should be a smaller ontology, e.g. created as a justification for a subsumption
    forgetOntology = "datasets/pizza.owl"

    # Decide on a method for the forgetter (check the papers of LETHE to understand the different options).
    # The default is 1, I believe.
    # 1 - ALCHTBoxForgetter
    # 2 - SHQTBoxForgetter
    # 3 - ALCOntologyForgetter
    method = "2" #

    #######update this txt file to forget more stuff
    # Choose the symbols which you want to forget.
    signature = "datasets/signature.txt"


    # 1. PRINT ALL SUBCLASSES (inputOntology):
    # print all subClass statements (explicit and inferred) in the inputOntology
    # --> uncomment the following line to run this function
    os.system('java -jar kr_functions.jar ' + 'printAllSubClasses' + " " + inputOntology)

    # 2. SAVE ALL SUBCLASSES (inputOntology):
    # save all subClass statements (explicit and inferred) in the inputOntology to file datasets/subClasses.nt
    # --> uncomment the following line to run this function
    os.system('java -jar kr_functions.jar ' + 'saveAllSubClasses' + " " + inputOntology)

    # 3. PRINT ALL EXPLANATIONS (inputOntology, inputSubclassStatements):
    # print explanations for each subClass statement in the inputSubclassStatements
    # --> uncomment the following line to run this function
    os.system('java -jar kr_functions.jar ' + 'printAllExplanations' + " " + inputOntology + " " + inputSubclassStatements)

    # 4. SAVE ALL EXPLANATIONS (inputOntology, inputSubclassStatements):
    # save explanations for each subClass statement in the inputSubclassStatements to file datasets/exp-#.owl
    # --> uncomment the following line to run this function
    os.system('java -jar kr_functions.jar ' + 'saveAllExplanations' + " " + inputOntology + " " + inputSubclassStatements)
    return forgetOntology,method,signature

def forgetting(forgetOntology,method,signature):
    #retrieve list of subclasses
    subclasses = extract_subclass()
    #subclasses = extract_subclass_class()

    #create signature file with only one subclass eachtime
    keys = ['duration','n_axioms','av_axioms','definers','n_restrictions'] 
    dict_output = {}
    for key in keys: 
        dict_output[key] = []

    for s in subclasses:              
        with open("datasets/signature.txt", "w") as sig:
            sig.write(s + "\n")
            print('forgetting ' + s + ' and generating result')
            # For running LETHE forget command:
            # --> uncomment the following line to run this function
        #extract insights from output
        #os.system('java -cp lethe-standalone.jar uk.ac.man.cs.lethe.internal.application.ForgettingConsoleApplication --owlFile ' + forgetOntology + ' --method ' + method  + ' --signature ' + signature)
        direct_output = subprocess.check_output('java -cp lethe-standalone.jar uk.ac.man.cs.lethe.internal.application.ForgettingConsoleApplication --owlFile ' + forgetOntology + ' --method ' + method  + ' --signature ' + signature, shell=True) #could be anything here.    
        #process output
        values = process_output(direct_output)
        for key,value in zip(keys,values):
            dict_output[key].append(value)

    dict_input = get_input_metrics(direct_output)  #metrics before iterations   
    return dict_input,dict_output,subclasses


def ranking(subclasses,dict_output):
    naxiom_sorted =[(subclasses[i].split('#')[1] , dict_output['n_axioms'][i]) for i in argsort(dict_output['n_axioms']) if len(subclasses[i].split('#'))>1]
    naverage_sorted =[(subclasses[i].split('#')[1] , dict_output['av_axioms'][i]) for i in argsort(dict_output['av_axioms']) if len(subclasses[i].split('#'))>1]
    return naxiom_sorted, naverage_sorted


def network_subclass():
    subclasses = []
    classes = []
    with open("datasets/subClasses.nt", "r") as sub:
        for line in sub:
            line1 = line.split()
            line2 = line1[0].replace("<", "")
            line3 = line2.replace(">", "")
           # if line3 not in subclasses:
            subclasses.append(line3)
            line2 = line1[2].replace("<", "")
            line3 = line2.replace(">", "")
            classes.append(line3)
    label_sub = [l.split('#')[1] for l in subclasses] 
    label_cla = []
    for l in classes:
        if l and len(l.split('#'))>1:
            label_cla.append(l.split('#')[1])
  
    
    G = nx.DiGraph()
    G.add_edges_from(zip(label_sub,label_cla))
    
    G_simple = nx.Graph()
    return G

def ranking_degree(G):
    in_degrees = list(G.in_degree(G.nodes()))
    in_degrees_sorted = array(in_degrees)[array([d[1] for d in in_degrees]).argsort()]

    out_degrees = list(G.out_degree(G.nodes()))
    out_degrees_sorted = array(out_degrees)[array([d[1] for d in out_degrees]).argsort()]
    
    return in_degrees,out_degrees,in_degrees_sorted, out_degrees_sorted


def forgetting_densely(forgetOntology,method,signature,subclasses_to_forget_sorted):
    #create signature file with only one subclass eachtime
    keys = ['duration','n_axioms','av_axioms','definers','n_restrictions'] 
    dict_output = {}
    for key in keys: 
        dict_output[key] = []

    #number of signatures I want to forget
    for K in range(1,10): #it becomes crazy at 10 and takes forever
        print('forgetting' +str(K) + 'highly connected signatures')
        with open("datasets/signature.txt", "w") as sig:
            for s in subclasses_to_forget_sorted[-K::]:        
                sig.write(s + "\n")
        # For running LETHE forget command:
        direct_output = subprocess.check_output('java -cp lethe-standalone.jar uk.ac.man.cs.lethe.internal.application.ForgettingConsoleApplication --owlFile ' + forgetOntology + ' --method ' + method  + ' --signature ' + signature, shell=True) #could be anything here.    
        #process output
        values = process_output(direct_output)
        for key,value in zip(keys,values):
            dict_output[key].append(value)
            
    dict_input = get_input_metrics(direct_output)  #metrics before iterations    
    return dict_input,dict_output

def forgetting_sparsely(forgetOntology,method,signature,subclasses_to_forget_sorted):
    #create signature file with only one subclass eachtime
    keys = ['duration','n_axioms','av_axioms','definers','n_restrictions'] 
    dict_output_mintomax = {}
    for key in keys: 
        dict_output_mintomax[key] = []

    #number of signatures I want to forget
    for K in range(1,10): 
        print('forgetting' +str(K) + 'lowly connected signatures')
        with open("datasets/signature.txt", "w") as sig: 
            for s in subclasses_to_forget_sorted[0:K]:       
                sig.write(s + "\n")
        # For running LETHE forget command:
        direct_output = subprocess.check_output('java -cp lethe-standalone.jar uk.ac.man.cs.lethe.internal.application.ForgettingConsoleApplication --owlFile ' + forgetOntology + ' --method ' + method  + ' --signature ' + signature, shell=True) #could be anything here.    
        #process output
        values = process_output(direct_output)
        for key,value in zip(keys,values):
            dict_output_mintomax[key].append(value)
            
    dict_input = get_input_metrics(direct_output)  #metrics before iterations 

    return dict_input,dict_output_mintomax