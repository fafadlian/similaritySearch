#!/bin/bash
#SBATCH --job-name=XGBSimilaritySearch
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=64
#SBATCH --time=96:00:00
#SBATCH --mem=128G
#SBATCH --mail-user=m.f.fadlian@sheffield.ac.uk
#SBATCH --mail-type=ALL
#SBATCH --output=output.%j.test.out

module load Anaconda3/2022.05
source activate similaritysearch
python SS_Test.py