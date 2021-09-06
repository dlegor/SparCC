# **SparCC** 

SparCC is a Python module for calculating correlations in compositional data (16S, metagenomics, etc.). This implementation is very similar to [original](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1002687), but enriched with dask and numba.

There are two ways of execution, using each *script step by step* or defining the required parameters from the *configuration file*. 

********************************
## **By Scripts** 
********************************

Scripts in the root SparCC directory can be called from the terminal command-line either by explicitly calling python (as is done in the usage examples below), or simply as an executable. The latter will require having execution permission for these file (e.g. chmod +x Compute_SparCC.py).

Help for any one for the scripts in the root SparCC directory is available by typing:
~~~python 
'python [script_name] - h'
~~~ 
in the command line. e.g.:

~~~bash
python Compute_SparCC.py -h
~~~

~~~bash
python MakeBootstraps.py -h
~~~

~~~bash
python PseudoPvals.py -h 
~~~

********************************
Execution by scripts example 
********************************

- The following lists the commands required for analyzing the included 'fake' dataset using the sparcc package, and generating all the files present in the subfolders of the example folder.

- The fake dataset contains simulated abundances of 50 otus in 200 samples, drawn at random from a multinomial log-normal distribution. The true basis correlations used to generate the data are listed in 'true_basis_cor.txt' in the example folder.

- Note that otu 0 is very dominant, and thus, using Pearson or Spearman correlations, appears to be negatively correlated with most other OTUs, though it is in fact not negatively correlated with any OTU.

Correlation Estimation:
------------------------

First, we'll quantify the correlation between all OTUs, using SparCC:

~~~bash
python Compute_SparCC.py  -n Experiment_SparCC -di example/fake_data.txt -ni 5 --save_cor=example/basis_corr/cor_sparcc.csv
~~~


Pseudo p-value Calculation:
---------------------------

Calculating pseudo p-values is done via a bootstrap procedure.
First make shuffled (w. replacement) datasets:

~~~bash
python MakeBootstraps.py example/fake_data.txt -n 5 -t permutation_#.csv -p example/pvals/
~~~

This will generate 5 shuffled datasets, which is clearly not enough to get meaningful p-values, and is used here for convenience.

A more appropriate number of shuffles should be at least a 100, which is the default value. 

Next, you'll have to run SparCC on each of the shuffled data sets. 
Make sure to use the exact same parameters which you used when running SparCC on the real data, name all the output files consistently, numbered sequentially, and with a '.txt'(or csv) extension.

* method one: one by one.
~~~bash
python SparCC.py example/pvals/permutation_0.txt -i 5 --cor_file=example/pvals/perm_cor_0.txt
python SparCC.py example/pvals/permutation_1.txt -i 5 --cor_file=example/pvals/perm_cor_1.txt
python SparCC.py example/pvals/permutation_2.txt -i 5 --cor_file=example/pvals/perm_cor_2.txt
python SparCC.py example/pvals/permutation_3.txt -i 5 --cor_file=example/pvals/perm_cor_3.txt
python SparCC.py example/pvals/permutation_4.txt -i 5 --cor_file=example/pvals/perm_cor_4.txt
~~~


* method two (bash code): all with a loop.

~~~bash
for i in `seq 0 4`; do python Compute_SparCC.py --name Experiment_PVals -di example/pvals/permutation_$i.csv --save_cor example/pvals/perm_cor_$i.csv  >> case_example.log; done
~~~

Above I'm simply called SparCC 5 separate times. Now that we have all the correlations computed from the shuffled datasets, we're ready to get the pseudo p-values.

Remember to make sure all the correlation files are in the same folder, are numbered sequentially, and have a '.txt' extension(or .csv).

The following will compute both one and two sided p-values.

~~~bash
python PseudoPvals.py example/basis_corr/cor_sparcc.csv example/pvals/perm_cor_#.csv 5 -o example/pvals/pvals_one_sided.csv -t one_sided

#another option 

#python PseudoPvals.py example/basis_corr/cor_sparcc.out example/pvals/perm_cor_#.txt 5 -o example/pvals/pvals.one_sided.txt -t two_sided
~~~

---
## **Run with configuration**
---
For this case, the *General_Execution.py* script is used. For its operation, all the necessary parameters must be defined in the configuratio.yml file.

**************************
## Run with configuration
**************************
To estimate SparCC in this way, you must fill in all the fields in the **configuration.yml** file. If you leave it as None, the value to run SparCC will be the default.

Required fields

~~~bash
# Correlation Calculation

name: 'experiment_sparCC' 
data_input: 'example/fake_data.txt'
method: 'sparcc'
n_iteractions: 5
x_iteractions: 10
threshold: 0.1
normalization: 'dirichlet'
log_transform: True
save_corr_file: 'example/cor_sparcc.csv' 
save_cov_file:  Null

# Pseudo p-value Calculation

num_simulate_data: 5
perm_template: 'permutation_#.csv' 
outpath: 'example/pvals/'
type_pvalues: 'one_sided'
outfile_pvals : 'example/pvals/pvals_one_sided.csv'

# Output file

name_output_file: 'sparcc_version1'

~~~
Only the following is required to run the script:

~~~python
python General_Execution.py 
~~~

The output with the previous configuration, would be the files:
* cor_sparcc.csv
* pvals_one_sided.csv

********************
## Kombucha dataset example
********************

There are 5 steps to process the data:

**Step 1 :** SparCC Estimation of the Otus.
~~~bash
python Compute_SparCC.py  -n Experiment_SparCC -di /home/dlegorreta/Documentos/ixulabs/4Cienegas/Data/T1B_Tapetes_secos-20191006T171745Z-001/T1B_Tapetes_secos/OTUs/filtered_otu_table_t1b.txt -xi 50  -ni 100 --save_cor=sparcc_output/cor_sparcc_tapetes.csv
~~~

**Step 2 :** Make Bootstraps with the Otus.
~~~bash
python MakeBootstraps.py /home/dlegorreta/Documentos/ixulabs/4Cienegas/Data/T1B_Tapetes_secos-20191006T171745Z-001/T1B_Tapetes_secos/OTUs/filtered_otu_table_t1b.txt -n 100 -t permutation_#.csv -p pvals/
~~~

**Step 3 :** SparCC estimation on all files from Step 2.
~~~bash
for i in `seq 0 99`; do python Compute_SparCC.py --name Experiment_PVals -di pvals/permutation_$i.csv --save_cor pvals/perm_cor_$i.csv --verbose False >> Pval_Tapetes.log; done
~~~

**Step 4 :** Estimation of P-test on all SparCC files from subsamples.
~~~bash
python PseudoPvals.py sparcc_output/cor_sparcc.csv pvals/perm_cor_#.csv 5 -o example/pvals/pvals_one_sided.csv -t one_sided
~~~

**Step 5 :** Take only the Otus with p-values ​​that satisfy the hypothesis test, that is, if the significance level is p = 0.05, those that are equal to or less than that value are rejected.

**Note:** This example can be run with the configuration file, you only need to define the parameters similar to the ones that were used.

*********
Refernce
*********

Detailed information about the algorithm can be found in the accompanying [publication](<http://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1002687>).  
