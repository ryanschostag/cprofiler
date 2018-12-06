# cprofiler
Command line utility and class module to run single file or files in batch through cProfile and store the data in csv files.

        cprofile_to_csv.py

        Extract performance data from functions in a Python scripts. Does not work on modules alone

        Note that invalid arguments are ignored.

        python cprofile_to_csv.py -v|--verbose -d|--directory [DIR] -r|--recurse -w|--working-dir -f|--file [FILE]

        -f --file                   Tells program to profile a single file
        -w --working-dir            Tells program to pull all files in working directory into a set
        -r --recurse                Recursively searches for files. Implies --all
        -v --verbose                Turns verbose on for additional print statements.
                                    Requires an additional option from this list or at least one file name
        -d --directory              Tells program to change to this directory

        Examples:

        python cprofile_to_csv.py

            Searches for Python files from the working directory. Runs performance analysis on them.

        python cprofile_to_csv.py -r

            Searches for Python files from the working directory all subfolders. Runs performance analysis on them.

            Also:

                python cprofile_to_csv.py --recursive

        Windows:    python cprofile_to_csv.py -d "\temp\py" -r -v
        UNIX:       python cprofile_to_csv.py -d "/tmp/py" -r -v

            Starts from directory specified by -d and recurses in verbose mode

        Windows:    python cprofile_to_csv.py --directory="\temp\py" -r -v
        UNIX:       python cprofile_to_csv.py --directory="/tmp/py" -r -v

            This does the same as above. --directory=[dir] is the alternative to -d [dir]

        Windows:    python cprofile_to_csv.py -f .\scriptsile_1.py
        UNIX:       python cprofile_to_csv.py -f ./scripts/file_1.py

            Profiles a single Python script

Dependencies:

Pythnon 3+

Potential Usage:

A subset of the dictonary, for example, can be loaded into a Pandas or Apache Spark DataFrame for analysis, visualization and reporting.
