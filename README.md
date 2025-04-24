# CSE583 Final Project – Auto Parallelization

This is the final project for CSE583. We extend [OMPAR](https://github.com/Scientific-Computing-Lab/OMPar.git), a compiler-based tool for identifying and generating parallelization opportunities in serial code, by incorporating dynamic analysis and memory access profiling.

## Building the tool

To build this tool, ensure that your system supports CUDA 12.1 before proceeding.

#### 1. Clone the repository:

```bash
git clone -b model https://github.com/ethansun168/cse583-project.git
cd OMPar
```

#### 2. Create and activate the Conda environment:

```bash
conda env create -f environment.yml
conda activate ompar_env
```

#### 3. Build the parser:

```bash
cd parser
./build.sh
```

## Usage

#### 1. Prepare your test code

Create a subfolder under demo/, and place your test file (named test.c) inside:

demo/<your_folder>/test.c

#### 2. Extract featrues via LLVM

Run the following to extract static, dynamic, and memory access features using LLVM:

```bash
cd OMPar
sh get_features.sh
```

Check that the following files are generated in your demo/<your_folder>/:

- static.txt
- dynamic.txt
- memory_access_count.txt

#### 3. Run the Prediction Model

Download the custom OMPify model weights from [here](https://drive.google.com/drive/folders/1tnJf9YvjpDLktVi23TkW-rpjqfdZoybf?usp=sharing), and place the .bin file inside the OMPify/ directory.

Run the model with:

```bash
python3 run_ompar.py --source_file demo/test1/mytest.c --static_file demo/test1/static.txt --dynamic_file demo/test1/dynamic.txt --memory_file demo/test1/memory_access_count.txt
```

## Training the Model

#### 1. Prepare the dataset

You can download the re-organized version (with loop ID) of the Open-OMP-Plus dataset used in our experiments from [here](https://drive.google.com/drive/folders/1p0-KupXmykfh_3bNbQnrHAUmsKGfD54T?usp=drive_link). Alternatively, you can prepare your own dataset following the same format. Each sample directory should contain the following files:

###### (1) W/O loop ID

- test.c: the full original source code
- code.c: contains only the loop(s) to analyze
- static.txt
- dynamic.txt
- memory_access_count.txt
- pragma.c: expected pragma annotations

To generate these files, place your original code in the appropriate directory and run `get_features.sh`.
Make sure to verify all paths inside the script are correctly set for your directory structure.

###### (2) W/loop ID

- test.c: the full original source code
- code.c: contains only the loop(s) to analyze
- ID.txt
- static.txt
- extracted_dynamic.txt
- memory_access_count.txt
- pragma.c

Steps:

1. Place your original `test.c` and corresponding `code.c` in the desired folder.
2. Run `run_all.sh` and `loop_id.py` in the `analysis/match/` directory to generate `ID.txt`.
3. Open `analysis/memory_access/unique.py` and:
   - Comment out Version 1
   - Uncomment Version 2
4. Run `get_features.sh` to generate static and memory features.

#### 2. Generate .json files

If you try to use our dataset, just run json_generator.py:

- Use verion 1 for dataset without loop ID
- Use version 2 for datasets with loop ID

#### 3. Train the model

Start training by running:

> ```bash
> python3 train.py
> ```
