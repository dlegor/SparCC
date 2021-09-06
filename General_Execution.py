#!/usr/bin/env python3
from pathlib import Path
import shutil
import yaml
import os
from wasabi import msg
import typer



def main(
    configuration_file: str = typer.Option('configuration.yml', help="Configuration File"),
    name : str = typer.Option('experiment_sparCC', help="Log Name"),
    data_input: str = typer.Option('example/fake_data.txt', help="Path file input"),
    method: str= typer.Option('sparcc', help=""),
    n_iteractions: int = typer.Option(2, "--niteractions", "-nit", help=""),   
    x_iteractions: int = typer.Option(2, "--xiteractions", "-xit", help=""),
    threshold:float = typer.Option(0.1,"--threshold","-th"),
    normalization:str=typer.Option('dirichlet'),
    log_transform:bool=typer.Option(True),
    save_corr_file:str=typer.Option("example/cor_sparcc.csv"),
    save_cov_file:str=typer.Option(None),
    num_simulate_data:int=typer.Option(3),
    perm_template:str=typer.Option('permutation_#.csv'),
    outpath:str=typer.Option('example/pvals/'),
    type_pvalues:str=typer.Option('one_sided'),
    outfile_pvals:str=typer.Option('example/pvals/pvals_one_sided.csv'),
    name_output_file:str=typer.Option('sparcc_test_version_kambucha')
    ):
    """
    Script for end-to-end execution of SparCC

    Executing all the SparCC steps together, it is 
    very important to configure the parameters in the 
    configuration.yml file. 

    Usage:
        $ python General_Execution.py

    Note: 
    Depending on the size of the given OTU matrix, it
    is the time it takes to calculate all the stages. 
    Please be careful that the process is not truncated 
    or canceled.

    """
    #Configuration params
    configuration_file=Path(configuration_file)
    if configuration_file.is_file():
        catalog=configuration_file.resolve()
        
        with open(catalog) as file:
            Conf_Cat=yaml.load(file,Loader=yaml.FullLoader)

        # Loading parameters
        name=Conf_Cat['name']
        data_input=Conf_Cat['data_input']
        method=Conf_Cat['method']
        n_iteractions=Conf_Cat['n_iteractions']
        x_iteractions=Conf_Cat['x_iteractions'] 
        threshold=Conf_Cat['threshold']
        normalization=Conf_Cat['normalization'] 
        log_transform=Conf_Cat['log_transform'] 
        save_corr_file=Conf_Cat['save_corr_file']  
        save_cov_file=Conf_Cat['save_cov_file'] 

        # Pseudo p-value Calculation
        num_simulate_data= Conf_Cat['num_simulate_data']
        perm_template= Conf_Cat['perm_template'] 
        outpath=Conf_Cat['outpath'] 
        type_pvalues=Conf_Cat['type_pvalues']
        outfile_pvals=Conf_Cat['outfile_pvals']

    #Covalence Matrix?
    if save_cov_file== None:
        #SparCC
        os.system(f'python Compute_SparCC.py  -n {name} -di {data_input} \
           -m {method} -ni {n_iteractions} -xi {x_iteractions} \
           -th {threshold} -no {normalization} --log {log_transform} \
           -scor {save_corr_file}')
    else:

        #SparCC
        os.system(f'python Compute_SparCC.py  -n {name} -di {data_input} \
           -m {method} -ni {n_iteractions} -xi {x_iteractions} \
           -th {threshold} -no {normalization} --log {log_transform} \
           -scor {save_corr_file} -scov {save_cov_file}')


    #MakeBoostraps
    os.system(f'python MakeBootstraps.py {data_input} -n {num_simulate_data} \
           -t {perm_template} -p {outpath}')

    #correlation files
    file_pvals=str(outpath)+str(perm_template)
    corr_file=str(outpath)+'perm_cor_#.csv'

    # #Iteraction in files
    for i in range(int(num_simulate_data)):
        print('#'*100)
        print(f'Iteration: {str(i)}')
        file_pvals1=file_pvals.replace('#',str(i))
        corr_file1=corr_file.replace('#',str(i))

        os.system(f'python Compute_SparCC.py  -n {name} -di {file_pvals1} \
             -m {method} -ni {n_iteractions} -xi {x_iteractions} \
             -th {threshold} -no {normalization} --log {log_transform} \
             -scor {corr_file1}')

    #Clean Files: perm_corr
    folder=Path(outpath)
    List_files_rm=list(folder.glob(perm_template.replace('#','*')))
    for f in List_files_rm:
        f.unlink()

    #Estimation of PValues
    print("#"*100)
    os.system(f'python PseudoPvals.py {save_corr_file} \
        {corr_file} {num_simulate_data} -o {outfile_pvals} \
        example/pvals/pvals_one_sided.csv -t {type_pvalues}')


    #Clean perm_cor_* files
    List_files_rm=list(folder.glob('perm_cor_*.csv'))
    for f in List_files_rm:
        f.unlink()

    #move log
    if Path(save_corr_file).parent.is_dir():
        output=Path(save_corr_file).parent/f'{name}.log'
        source=Path(f'{name}.log')
        shutil.move(source,output)



    print(' '*50+'Execution Ended'+' '*50)
    print("#"*100)


if __name__ == "__main__":
    typer.run(main)
