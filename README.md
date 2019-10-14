# ADD_CMAP.py
## Add CMAP parameters into original AMBER prmtop file

&ensp;&ensp;Inorder to obtain a accurate descripion of intrinscally disorder proteins(IDPs) ensembles, grid-based energy correction maps (CMAP) method
<sup>[1]</sup> was applied in MD simulation to improve the sampling of backbond dihedrals of IDPs which have high heterogeneous conformers.
Therefore, several IDP-sepcific force fields were developed based on the classical AMBER force fields by adding CMAP energy terms in MD
simulations, such as ff99IDPs<sup>[2][3]</sup>, ff14IDPs<sup>[4]</sup>, ff14IDPSFF<sup>[5]</sup>.  

&ensp;&ensp;This script is used to add CMAP parameters into the prmtop file which is generated by *tleap* module of AMBER packages. This script provides interacting command lines to add CMAP parameters to the residues of interest and the silent mode to skip these interacting command lines and add CMAP parameters to all residues.    

Usage: python ADD-CMAP.py -p amber.prmtop -c CMAP_parameters -o amber_CMAP.prmtop [-s]  

    -p    prmtop files generated by tleap with  
            leaprc.ff99SB (if you want ot use ff99IDPs force field)
            leaprc.ff14SB (if you want ot use ff14IDPs or ff14IDPSFF force field)
            leaprc.ff03.r1 (if you want to use ff03CMAP force field)
    -c    CMAP parameter file
    -o    prmtop files within CMAP parameters
    -s    silent mode

Please cite the following papers if you are using this script:  

<sup>[1]</sup> MacKerell A. D., et al. Improved treatment of the protein backbone in empirical force fields. J. Am. Chem. Soc. 2004, 126, 698-699. (CMAP Method)  
<sup>[2]</sup> Wang W., et al. New force field on modeling intrinsically disordered proteins. Chem. Biol. Drug Des. 2014, 84, 253-269. (ff99IDPs force field)  
<sup>[3]</sup> Ye W., et al. Test and Evaluation of ff99IDPs Force Field for Intrinsically Disordered Proteins. J. Chem. Inf. Model. 2015, 55, 1021-1029. (ff99IDPs force field)  
<sup>[4]</sup> Song D., et al. ff14IDPs force field improving the conformation sampling of intrinsically disordered proteins. Chem. Biol. Drug Des. 2017, 89, 5-15. (ff14IDPs force field)  
<sup>[5]</sup> Song D., et al. The IDP-Specific Force Field ff14IDPSFF Improves the Conformer Sampling of Intrinsically Disordered Proteins. J. Chem. Inf. Model. 2017, 57, 1166-1178. (ff14IDPSFF force field)  
