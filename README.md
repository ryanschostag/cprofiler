# cprofiler
Command line utility and class module to run single file or files in batch through cProfile and store the data in CSV files, one per file, with a time stamp YYYY-MM-DD-HH-MM-SS.csv at the end, suitable for parsing and importing the data in each CSV into a time series data set for performance testing data analytics and machine learning. 

        cprofiler.py

        Extract performance data from functions in a Python scripts.

        Note that invalid arguments are ignored.

        python cprofile_to_csv.py -v|--verbose -d|--directory [DIR] -r|--recurse -w|--working-dir -f|--file [FILE]

        -f --file                   Tells program to profile a single file
        -w --working-dir            Tells program to pull all files in working directory into a set
        -r --recurse                Recursively searches for files. Implies --all
        -v --verbose                Turns verbose on for additional print statements.
                                    Requires an additional option from this list or at least one file name
        -d --directory              Tells program to change to this directory

        Examples:

        python cprofiler.py

            Searches for Python files from the working directory. Runs performance analysis on them.

        python cprofiler.py -r

            Searches for Python files from the working directory all subfolders. Runs performance analysis on them.

            Also:

                python cprofiler.py --recursive

        Windows:    python cprofiler.py -d "\temp\py" -r -v
        UNIX:       python cprofiler.pyy -d "/tmp/py" -r -v

            Starts from directory specified by -d and recurses in verbose mode

        Windows:    python cprofiler.py --directory="\temp\py" -r -v
        UNIX:       python cprofiler.py --directory="/tmp/py" -r -v

            This does the same as above. --directory=[dir] is the alternative to -d [dir]

        Windows:    python cprofiler.py -f .\scriptsile_1.py
        UNIX:       python cprofiler.py -f ./scripts/file_1.py

            Profiles a single Python script

Dependencies:

Python 3+

