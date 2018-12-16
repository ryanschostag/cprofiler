"""
cprofiler.py

Classes:

PyProfiler

Description:    PyProfiler is a class of methods that profile one or more Python scripts and stores
                the data in a csv file per script profiled. The flat files assist with data
                analystics and machine learning (making predictions of performance increases or
                decreases. Also, helps an individual developer to monitor ones own progress.
"""

# pylint: disable=too-many-lines,literal-comparison
import subprocess
from os import path, chdir
from sys import argv, platform
from time import time
from glob import glob
import re
import csv
import datetime

class PyProfiler:
    """
    Methods:

    _arg_parser
    _args_or_argv
    _change_directories
    _cprofile_bytes_to_string
    _cprofile_field_structure_tester
    _cprofile_list_of_dicts_to_csv
    _create_cprofile_dictionary
    _float_or_int_tester
    _get_file_list
    _help_args_checker
    _help_message
    _process_profile_dictionary
    _run_cprofile
    _set_verbosity
    _settings_check
    cprofile_file_data
    defaults
    prep_for_cprofile_list_of_dicts_to_csv
    print_dict
    run_performance_tests
    test_arg_parser
    test_args_or_argv
    test_change_directories
    test_cprofile_bytes_to_string
    test_cprofile_file_data
    test_cprofile_list_of_dicts_to_csv
    test_create_cprofile_dictionary
    test_get_file_list
    test_help_args_checker
    test_help_message
    test_prep_for_cprofile_list_of_dicts_to_csv
    test_run_cprofile
    test_run_performance_tests
    test_set_verbosity
    timer
    """

    def __init__(self):
        super(PyProfiler, self).__init__()
        self.verbose = False
        self.separator = '\\' if platform == 'win32' else '/'
        self.switches = ('-w', '--working-dir', '-r', '--recurse', '-h', '--help', '-d',
                         '--directory', '-v', '--verbose', '-f', '--file')

    def _help_message(self):
        # pylint: disable=anomalous-backslash-in-string
        return """
        {0}
        
        Extract performance data from functions in a Python scripts.
        
        Note that invalid arguments are ignored.
        
        python {0} -v|--verbose -d|--directory [DIR] -r|--recurse -w|--working-dir -f|--file [FILE]
        
        -f --file                   Tells program to profile a single file
        -w --working-dir            Tells program to pull all files in working directory into a set
        -r --recurse                Recursively searches for files. Implies --all 
        -v --verbose                Turns verbose on for additional print statements. 
                                    Requires an additional option from this list or at least one\
 file name
        -d --directory              Change to the specified directory as starting point
                            
        Examples:
        
        python {0}
        
            Searches for Python files from the working directory. Runs performance analysis on them. 
            
        python {0} -r
        
            Searches for Python files from the working directory all subfolders. Runs performance \
analysis on them.
            
            Also:
            
                python {0} --recursive
                
        Windows:    python {0} -d "\\temp\\py" -r -v
        UNIX:       python {0} -d "/tmp/py" -r -v
        
            Starts from directory specified by -d and recurses in verbose mode
            
        Windows:    python {0} --directory="\\temp\py" -r -v
        UNIX:       python {0} --directory="/tmp/py" -r -v
        
            This does the same as above. --directory=[dir] is the alternative to -d [dir]
            
        Windows:    python {0} -f .\scripts\file_1.py
        UNIX:       python {0} -f ./scripts/file_1.py
        
            Profiles a single Python script
        
        """.format(argv[0].split(self.separator)[-1])

    @staticmethod
    def _float_or_int_tester(string_to_test, verbose=False):
        # tests whether item is a string, float or int, and returns the result as a converted item
        # pylint: disable=too-many-branches
        if verbose:
            print('Verbose: Enter _float_or_int_tester()')

        if not isinstance(string_to_test, str):
            return string_to_test

        two_nums = []
        if '/' in string_to_test:
            two_nums.append(string_to_test.split('/'))

        if '.' not in string_to_test:
            try:
                if two_nums and (int(two_nums[0]) > int(two_nums[1])):
                    string_to_test = int(two_nums[0])
                elif two_nums and (int(two_nums[0]) < int(two_nums[1])):
                    string_to_test = int(two_nums[1])
                else:
                    string_to_test = int(string_to_test)
                return string_to_test
            except ValueError as v_err:
                if verbose:
                    print(v_err)
            except TypeError as t_err:
                if verbose:
                    print(t_err)

        try:
            string_to_test = float(string_to_test)
            return string_to_test
        except ValueError as err:
            if verbose:
                print(err)
            return string_to_test

    @staticmethod
    def _run_cprofile(file_name, settings):
        # Run cprofile on the given file
        # pylint: disable=no-else-return
        verbose = settings['-v']

        if verbose:
            print('Verbose: Enter _run_cprofile()')

        if path.isfile(file_name):
            if verbose:
                print('Verbose: Exit _run_cprofile()')
            return subprocess.Popen('python -m cProfile -s cumtime ' + file_name,
                                    stdout=subprocess.PIPE).stdout.read().split(b'\r\n'), file_name
        else:
            if verbose:
                print('Verbose: Exit _run_cprofile()')
            return False

    @staticmethod
    def _cprofile_bytes_to_string(bytes_objects):
        # Takes list of bytes objects, converts to string and returns the list of strings
        return [str(i).replace('b\'', '').replace('b"', '') for i in bytes_objects]

    def _cprofile_field_structure_tester(self, item_to_test: list, verbose=False):
        # Accepts a list of objects and tests whether their type has the pattern
        # int, float, float, float, float, string
        # returns a tuple of matching strings
        # pylint: disable=too-many-branches

        if verbose:
            print('Verbose: Enter cprofile_field_structure_tester with item_to_test={}'
                  .format(item_to_test))

        if not isinstance(item_to_test, list):
            if verbose:
                print('Error: {} is not of type <list>. Got type <{}> instead'
                      .format(item_to_test, type(item_to_test)))
            return []

        item_list_length = len(item_to_test)

        type_list = []
        for item in item_to_test:
            type_list.append(type(item))

        if verbose:
            print('Verbose: type_list = {}'.format(type_list))
            print('Verbose: item_list_length = {}'.format(item_list_length))

        structure = {
            0: int,
            1: float,
            2: float,
            3: float,
            4: float,
            5: str,
        }

        test_tuple = ()
        results_tuple = ()
        comparison = (int, float, float, float, float, str)

        if len(item_to_test) != len(structure.values()):
            if verbose:
                print('Verbose: Exit cprofile_field_structure_tester length {} != {}'
                      .format(len(item_to_test), len(structure.values())))
            return False

        for position, item in enumerate(item_to_test):
            if isinstance(self._float_or_int_tester(item, verbose=verbose), structure[position]):
                test_tuple += (type(structure[position](item)),)
                results_tuple += (structure[position](item),)

        for position, item in enumerate(test_tuple):
            if item == comparison[position]:
                continue
            else:
                if verbose:
                    print('Verbose: Exit cprofile_field_structure_tester as False')
                return False

        if verbose:
            print('Verbose: Exit cprofile_field_structure_tester with results_tuple: {}'
                  .format(results_tuple))

        return results_tuple

    def _create_cprofile_dictionary(self, cprofile_list, file, verbose=False):
        # Takes list of strings and returns a dictionary
        # pylint: disable=too-many-locals

        _, file_name = path.split(file)
        data_dict = {
            file_name: {
                'total_function_calls': None,
                'total_primitive_calls': None,
                'total_function_call_seconds': None,
            }
        }

        func_calls_regex = r"\d+ \w+ calls"
        c_func_calls_regex = re.compile(func_calls_regex)
        stats_regex = r"([\d+ ])+"
        func_file_list = []
        line_no_list = []
        func_name_list = []
        n_calls_list = []
        tot_time_list = []
        tot_time_percall_list = []
        cum_time_list = []
        cum_time_per_call = []

        for i in cprofile_list:
            if re.findall(c_func_calls_regex, i):
                if 'function' in i.split():
                    data_dict[file_name]['total_function_calls'] = float(i.split()[0])
                    data_dict[file_name]['total_primitive_calls'] = 0.0
                    data_dict[file_name]['total_function_call_seconds'] = float(i.split()[-2])
                if 'function' and 'primitive' in i.split():
                    data_dict[file_name]['total_primitive_calls'] = float(
                        i.split()[3].replace('(', ''))
            if re.findall(stats_regex, i):
                i_tuple = self._cprofile_field_structure_tester(i.split(), verbose=verbose)
                if i_tuple:
                    func_file_list.append(str(i_tuple[5]).split(':')[0])
                    line_no_list.append(int(str(i_tuple[5]).split(':')[1].split('(')[0]))
                    func_name_list.append(str(i_tuple[5]).split('(')[1].replace(')\'', ''))
                    n_calls_list.append(i_tuple[0])
                    tot_time_list.append(i_tuple[1])
                    tot_time_percall_list.append(i_tuple[2])
                    cum_time_list.append(i_tuple[3])
                    cum_time_per_call.append(i_tuple[4])

        for i in cprofile_list:
            if re.findall(stats_regex, i):
                i_tuple = self._cprofile_field_structure_tester(i.split(), verbose=verbose)
                if i_tuple:
                    data_dict[file_name]['function_stats'] = {
                        'func_file': func_file_list,
                        'func_file_line_no': line_no_list,
                        'func_name': func_name_list,
                        'ncalls': n_calls_list,
                        'tottime': tot_time_list,
                        'tottime_percall': tot_time_percall_list,
                        'cumtime': cum_time_list,
                        'cumtime_percall': cum_time_per_call,
                    }
        return data_dict

    @staticmethod
    def defaults():
        """
        Default settings dictionary
        """
        return {
            '-d': None,
            '--directory': None,
            '-w': False,
            '--working-dir': False,
            '-r': False,
            '--recurse': False,
            '-f': None,
            '--file': None,
            '-h': False,
            '--help': False,
            '-v': False,
            '--verbose': False,
        }

    @staticmethod
    def _args_or_argv(args=None):
        # Checks for argv or otherwise takes a list
        if not isinstance(args, list) and len(argv) == 1:
            raise TypeError(
                '_args_or_argv(args): Expected <list>. Got {} instead. sys.argv = {}'.format(
                    type(args), argv))
        elif (len(argv) == 1 and len(args) != 0) and args[0] == argv[0]:
            return argv[1:], 'argv'
        elif args:
            return args, 'args'
        else:
            raise ValueError(
                '_args_or_argv(args): <list> or <sys.argv> cannot be empty.'
            )

    def _check_for_other_arg(self, arg_list, base_arg_1, base_arg_2, verbose=False):
        # Checks if there is another switch in the arg_list
        # If so, it returns the help settings

        if verbose:
            print('Enter _check_for_other_arg()')

        if base_arg_1 in arg_list or base_arg_2 in arg_list:
            other_arg = []
            for position, switch in enumerate(self.switches):
                if switch == base_arg_1 or switch == base_arg_2:
                    continue
                elif switch in arg_list:
                    other_arg.append(True)
            if True not in other_arg:
                if verbose:
                    print('Verbose: Invalid setting: "{}" or "{}" requires another switch'.format(
                        base_arg_1, base_arg_2))
                    print('Verbose: Exit _check_for_other_arg()')
                return self._reset_settings_for_help()

    def _arg_parser(self, arg_list=None, flag=None, verbose=False):
        # pylint: disable=too-many-branches
        """
        Processes input from command line or list
        :param arg_list: <list> expected. None by default.
        :param flag: <string> or <None> (default). If <string> 'args' or 'argv' expected.
        :param verbose: True for extra print statements.
        :return: dictionary of configured settings
        """

        if verbose:
            print('Verbose: Enter _arg_parser()')

        if not isinstance(arg_list, list):
            raise TypeError('_arg_parser() requires a list')

        if not isinstance(flag, str):
            raise TypeError(
                '_arg_parser(flag): Expected <string>. Got {0} instead.'.format(type(flag))
            )

        if flag not in ('argv', 'args'):
            raise ValueError(
                '_arg_parser(flag): Expected "args" or "argv". Got {} instead'.format(flag)
            )

        args_dict = self.defaults()

        for index, item in enumerate(arg_list):
            if item.lower() in self.switches:
                arg_list[index] = item.lower()

        valid = []
        for item in self.switches:
            if item not in arg_list:
                valid.append(False)
            else:
                valid.append(True)

        if True not in valid:
            if verbose:
                print('Verbose: Exit _arg_parser()')
            raise ValueError('_arg_parser(arg_list): No valid arguments detected')
        elif verbose:
            print('Verbose: _arg_parser(arg_list): Contains valid arguments')

        # Sanitize argument list to prevent process when invalid settings are detected
        if '-h' in arg_list or '--help' in arg_list:
            if verbose:
                print('Verbose: Help Detected: Returning settings with only Help set to True')
                print('Verbose: Exit _arg_parser()')
            return self.test_reset_settings_for_help()

        if '-r' in arg_list and '-w' in arg_list:
            if verbose:
                print('Verbose: Invalid settings: "-w" and "-r" cannot be together')
                print('Verbose: Exit _arg_parser()')
            return self.test_reset_settings_for_help()

        if '--recurse' in arg_list and '-w' in arg_list:
            if verbose:
                print('Verbose: Invalid settings: "-w" and "--recurse" cannot be together')
                print('Verbose: Exit _arg_parser()')
            return self.test_reset_settings_for_help()

        if '-r' in arg_list and '--working-dir' in arg_list:
            if verbose:
                print('Verbose: Invalid settings: "--working-dir" and "-r" cannot be together')
                print('Verbose: Exit _arg_parser()')
            return self.test_reset_settings_for_help()

        if self._reset_settings_for_help() == self._check_for_other_arg(
                arg_list=arg_list, base_arg_1='-v', base_arg_2='--verbose',  verbose=verbose):
            return self._reset_settings_for_help()

        if self._reset_settings_for_help() == self._check_for_other_arg(
                arg_list=arg_list, base_arg_1='-d', base_arg_2='--directory',  verbose=verbose):
            return self._reset_settings_for_help()

        # pylint: disable=consider-iterating-dictionary
        for key in args_dict.keys():
            if key in arg_list:
                if key == '-d':
                    if verbose:
                        print('Verbose: -d found')
                    directory_index = arg_list.index(key)
                    if arg_list.index(arg_list[-1]) < directory_index+1:
                        raise SyntaxError('-d requires a space and path name')
                    args_dict[key] = arg_list[directory_index+1]
                    args_dict['--directory'] = arg_list[directory_index+1]
                elif key == '--directory':
                    if verbose:
                        print('Verbose: --directory found')
                    directory_index = arg_list.index(key)
                    if arg_list.index(arg_list[-1]) < directory_index+1:
                        raise SyntaxError('--directory requires a space and path name')
                    args_dict[key] = arg_list[directory_index+1]
                    args_dict['-d'] = arg_list[directory_index+1]
                elif key == '-f':
                    if verbose:
                        print('Verbose: -f found')
                    file_index = arg_list.index(key)
                    if arg_list.index(arg_list[-1]) < file_index+1:
                        raise SyntaxError('-f requires a space and file path')
                    args_dict[key] = arg_list[file_index+1]
                    args_dict['--file'] = arg_list[file_index+1]
                elif key == '--file':
                    if verbose:
                        print('Verbose: --file found')
                    file_index = arg_list.index(key)
                    if arg_list.index(arg_list[-1]) < file_index+1:
                        raise SyntaxError('--file requires a space and file path')
                    args_dict[key] = arg_list[file_index+1]
                    args_dict['-f'] = arg_list[file_index+1]
                elif key == '-w':
                    if verbose:
                        print('Verbose: -w found')
                    args_dict[key] = True
                    args_dict['--working-dir'] = True
                elif key == '--working-dir':
                    if verbose:
                        print('Verbose: --working-dir found')
                    args_dict[key] = True
                    args_dict['-w'] = True
                elif key == '-r':
                    if verbose:
                        print('Verbose: -r found')
                    args_dict[key] = True
                    args_dict['--recurse'] = True
                elif key == '--recurse':
                    if verbose:
                        print('Verbose: --recurse found')
                    args_dict[key] = True
                    args_dict['-r'] = True
                elif key == '-v':
                    if verbose:
                        print('Verbose: -v found')
                    args_dict[key] = True
                    args_dict['--verbose'] = True
                elif key == '--verbose':
                    if verbose:
                        print('Verbose: --verbose found')
                    args_dict[key] = True
                    args_dict['-v'] = True

        if verbose:
            print('Verbose: Exit _arg_parser()')

        return args_dict

    def _settings_check(self, func_name: str, settings: dict):
        # Validates the settings and raises errors in case of issues
        if not isinstance(func_name, str):
            raise TypeError(
                '_settings_check(func_name): Expected <string>. Got {} instead.'.format(
                    type(func_name)
                )
            )

        if func_name is None or func_name == '':
            raise ValueError(
                '_settings_check(func_name): Value cannot be empty or null.'
            )

        if not isinstance(settings, dict):
            raise TypeError(
                '{0}(settings): Expected <dict>. Got "{1}" instead.'.format(
                    func_name, type(settings))
            )

        if not settings:
            raise ValueError(
                '_{0}(settings): Settings cannot be empty'.format(func_name)
            )

        if settings.keys() != self.defaults().keys():
            raise KeyError(
                '{0}(settings): Invalid settings detected.'.format(func_name)
            )

        return True

    def _reset_settings_for_help(self):
        # provides settings with help information
        settings = self.defaults()
        settings['--help'] = True
        settings['-h'] = True
        return settings

    def _set_verbosity(self, settings):
        # sets the verbose level to True or False
        self._settings_check(func_name='_set_verbosity', settings=settings)
        if settings['-v'] is True or settings['--verbose'] is True:
            return True
        else:
            return False

    def _change_directories(self, settings):
        # If --directory or -d is True, changes to that directory
        self._settings_check(func_name='_change_directories', settings=settings)

        if settings['-d'] is not None:
            chdir(settings['-d'])
            return True
        elif settings['--directory'] is not None:
            chdir(settings['--directory'])
            return True
        elif settings['-d'] is None and settings['--directory'] is None:
            if settings['-v'] is True or settings['--verbose'] is True:
                print('Verbose: _change_directories: Directory blank. Using working directory.')
            working_directory, _ = path.split(argv[0])
            chdir(working_directory)

    def _get_file_list(self, settings):
        # Return s list of files in accordance with the given settings
        self._settings_check(func_name='_get_file_list', settings=settings)

        if settings['-r'] is True or settings['--recurse'] is True:
            return glob('**/*.py', recursive=True)
        elif settings['-w'] is True or settings['--working-dir'] is True:
            return glob('*.py', recursive=False)
        elif settings['-f'] is not None or settings['--file'] is not None:
            return [settings['-f']]
        else:
            raise ValueError(
                '_get_file_list(settings): Did not specify to recurse or use working directory.'
            )

    def timer(self, block_name: str, start: float, rounder: int=7, verbose: bool=False):
        """
        Timer method for calculating time a function or block of code takes to execute
        :param block_name: <string>
        :param start: <float> Output of time.time()
        :param rounder: <int> Integer to pass to round()
        :param verbose: Turne verbose off or on with False or True, respectively
        :return: <string> time_log: "[block_name] ==> [value] seconds [value] minutes [value] hours"
        """

        if not isinstance(block_name, str):
            raise TypeError(
                'timer(block_name): Expected <string>. Got {} instead'.format(type(block_name))
            )

        if not isinstance(start, float):
            raise TypeError(
                'timer(start): Expected <float>. Got {} instead'.format(type(start))
            )

        if not isinstance(rounder, int):
            raise TypeError(
                'timer(rounder): Expected <int>. Got {} instead'.format(type(rounder))
            )

        if not isinstance(verbose, bool):
            raise TypeError(
                'timer(verbose): Expected <bool>. Got {} instead'.format(type(verbose))
            )

        if self.verbose or verbose:
            print('Verbose: Enter timer() with: block_name={0} start={1} rounder={2}'
                  .format(block_name, start, rounder))

        end = time() - start

        time_log = '{0} ==> {1} seconds {2} minutes {3} hours' \
            .format(block_name, round(end, rounder),
                    round(end/60, rounder), round(end/60/60, rounder))

        if self.verbose or verbose:
            print('Verbose: Exit timer()')

        return time_log

    def print_dict(self, dictionary, existing_dict=None, additional_spacing=15, list_view=False,
                   nest_count=0):
        # print dictionary of dictionaries recursively

        if not dictionary:
            raise ValueError('print_dict(dictionary={}) cannot be an an empty dictionary'
                             .format(dictionary))
        if existing_dict is None:
            existing_dict = {}

        tab = '\t' * nest_count

        def print_dict_key_lengths(d):
            # finds the lengths of all keys in dictionary(ies)
            lengths = ()
            for k1, v1 in d.items():
                if isinstance(v1, dict):
                    return print_dict_key_lengths(v1)
                else:
                    lengths += (len(str(k1)),)
            return max(lengths)

        max_length = print_dict_key_lengths(dictionary) + additional_spacing
        for k, v in dictionary.items():
            if not isinstance(v, dict):
                existing_dict[k] = v
                if list_view and isinstance(v, list):
                    print(tab + str(k).ljust(max_length))
                    for i in v:
                        print(tab + '\t' + str(i).ljust(max_length))
                else:
                    print(tab + str(k).ljust(max_length) + str(v).ljust(max_length))
            else:
                print(tab + str(k).ljust(max_length))
                self.print_dict(dictionary=v, existing_dict=existing_dict, list_view=list_view,
                                nest_count=nest_count+1)

    def _process_profile_dictionary(self, old_dict, file_list=None, new_dict=None):
        if new_dict is None:
            new_dict = {}

        if file_list is None:
            file_list = []

        for k, v in old_dict.items():
            if k.endswith('.py'):
                file_list.append(k+'.csv')

            if not isinstance(v, dict):
                new_dict[k] = v
            else:
                self._process_profile_dictionary(v, new_dict)

        return new_dict

    def cprofile_file_data(self, cprofile_dict):
        """Returns a list of function_name, function_data tuples

        function_name is a string, and function_data is a list of dictionaries
        that will turn into lines in the csv writer.
        """
        output = []
        for file_name, dict_value in cprofile_dict.items():
            file_dictionaries = []

            function_stats = dict_value['function_stats']
            # The length of one of the lists in the function_stats dictionary
            len_of_stat = len(function_stats[list(function_stats)[0]])

            d = {total: dict_value[total] for total in ['total_function_calls',
                                                        'total_primitive_calls',
                                                        'total_function_call_seconds']}
            for index in range(len_of_stat):
                for stat in ['func_file', 'func_file_line_no', 'func_name', 'ncalls', 'tottime',
                             'tottime_percall', 'cumtime', 'tottime_percall', 'cumtime',
                             'cumtime_percall']:
                    d[stat] = function_stats[stat][index]

                if index == 1:
                    d['total_function_calls'] = d['total_primitive_calls'] = \
                        d['total_primitive_calls'] = None

                file_dictionaries.append(d.copy())
            output.append((file_name, file_dictionaries))

        return output

    def prep_for_cprofile_list_of_dicts_to_csv(self, test_file_dict_tuples):
        # preps data for cprofile_transform_list_of_dicts
        for file_data in test_file_dict_tuples:
            list_of_dictionary_lines = file_data[1]
            file_name = file_data[0].split('.')[0] + '-' + datetime.datetime.today().strftime(
                '%Y-%m-%d-%H-%M-%S') + '.csv'
            self._cprofile_list_of_dicts_to_csv(list_of_dictionary_lines, file_name)

    def _cprofile_list_of_dicts_to_csv(self, dict_lines: list, file_name: str):
        """
        Writes a list of dictionaries to a csv file using keys as columns and
        values as rows
        :param: dict_lines: <list> list of dictionaries
        :param: file_name: <string> name of the csv file
        """
        if isinstance(dict_lines, list) and dict_lines:
            csv_columns = dict_lines[0].keys()
            with open(file_name, 'w', newline='') as output_file:
                w = csv.DictWriter(output_file, fieldnames=csv_columns)
                w.writeheader()
                for dictionary in dict_lines:
                    w.writerow(dictionary)
        else:
            raise ValueError("Requires a nonempty list of dictionaries")

    def _help_args_checker(self, settings):
        # Checks the settings for -h and --help and if they are True prints help_messsage
        self._settings_check(func_name='_help_arg_checker', settings=settings)

        if settings['-h'] is True or settings['--help'] is True:
            return "Help!"

    def run_performance_tests(self, arguments=argv, verbose=False):
        """
        Main performance test function. Runs various helper functions to extract output,
        parse the data, and return data in a data structure for analysis and reporting
        :param arguments: <list> or <sys.argv> type. Default is sys.argv. Allows using list
                            for unit testing or using this as a module in another application.
        :param verbose: True or False
        :return: dictionary with values as list of tuples
        """
        start = time()

        if verbose:
            print('Verbose: Enter run_performance_tests()')

        working_dir, _ = path.split(argv[0])
        chdir(working_dir)

        args, flag = self._args_or_argv(args=arguments)
        settings = self._arg_parser(arg_list=args, flag=flag, verbose=verbose)
        verbose = self._set_verbosity(settings=settings)
        self._change_directories(settings=settings)

        if (not args or len(argv) == 1) or (self._help_args_checker(settings=settings) == 'Help!'):
            print(self._help_message())
            exit()

        files = self._get_file_list(settings=settings)

        if verbose:
            print('Verbose: files: {}'.format(files))

        master_dict = {}
        for p, i in enumerate(files):
            print('Processing file: {}'.format(i))
            cprofile_bytes_list, file_name = self._run_cprofile(file_name=i, settings=settings)
            cprofile_string_list = self._cprofile_bytes_to_string(cprofile_bytes_list)
            master_dict.update(self._create_cprofile_dictionary(cprofile_list=cprofile_string_list,
                                                                file=file_name, verbose=verbose))
        if verbose:
            print(self.timer(block_name='run_performance_tests', start=start, verbose=verbose))
            print('Verbose: Exit run_performance_tests()')

        return master_dict

    def test_get_file_list(self, settings):
        # returns a list of files
        print(settings)
        if settings['-r'] is True or settings['--recurse'] is True:
            return ['setup.py', '__init__.py', 'Array.py', 'conversions_file.py',
                    'cprofile_to_csv.py', 'pycam.py', 'pycam_test_helper.py', 'pylogger.py',
                    'pylogger_class.py', 'setup.py', '__init__.py', 'tests___init__.py',
                    'tests_integrationtests_integration_tests_pylogger.py',
                    'tests_integrationtests_integration_tests_pylogger_class.py',
                    'tests_unittests_pycam_test_helper_test.py',
                    'tests_unittests_pycam_test_helper_unit_test.py',
                    'tests_unittests_pylogger_class_unit_test.py',
                    'tests_unittests_pylogger_unit_test.py', 'tests_unittests_tests.py',
                    'tests_unittests___init__.py']
        elif settings['-w'] is True or settings['--working-dir'] is True:
            return ['setup.py', '__init__.py']
        elif settings['-f'] is not None or settings['--file'] is not None:
            return [settings['-f']]
        else:
            raise ValueError(
                'test_get_file_list(settings): -r|--recurse, -w|--working-dir, or -f|--file must \
be specified.')

    # Test functions for Unit Testing
    def test_help_message(self):
        # pylint: disable=anomalous-backslash-in-string
        return """
        {0}
        
        Extract performance data from functions in a Python scripts. 
        
        Note that invalid arguments are ignored.
        
        python {0} -v|--verbose -d|--directory [DIR] -r|--recurse -w|--working-dir -f|--file [FILE]
        
        -f --file                   Tells program to profile a single file
        -w --working-dir            Tells program to pull all files in working directory into a set
        -r --recurse                Recursively searches for files. Implies --all 
        -v --verbose                Turns verbose on for additional print statements. 
                                    Requires an additional option from this list or at least one\
 file name
        -d --directory              Change to the specified directory as starting point
                            
        Examples:
        
        python {0}
        
            Searches for Python files from the working directory. Runs performance analysis on them. 
            
        python {0} -r
        
            Searches for Python files from the working directory all subfolders. Runs performance \
analysis on them.
            
            Also:
            
                python {0} --recursive
                
        Windows:    python {0} -d "\\temp\\py" -r -v
        UNIX:       python {0} -d "/tmp/py" -r -v
        
            Starts from directory specified by -d and recurses in verbose mode
            
        Windows:    python {0} --directory="\\temp\py" -r -v
        UNIX:       python {0} --directory="/tmp/py" -r -v
        
            This does the same as above. --directory=[dir] is the alternative to -d [dir]
            
        Windows:    python {0} -f .\scripts\file_1.py
        UNIX:       python {0} -f ./scripts/file_1.py
        
            Profiles a single Python script
        
        """.format(argv[0].split(self.separator)[-1])

    def test_settings_check(self, func_name: str, settings: dict):
        """
        Validates the settings and raises errors in case of issues
        :param func_name: <string>
        :param settings: <dict>
        :return: True if no error, raises errors
        """
        if not isinstance(func_name, str):
            raise TypeError(
                '_settings_check(func_name): Expected <string>. Got {} instead.'.format(
                    type(func_name)
                )
            )

        if func_name is None or func_name == '':
            raise ValueError(
                '_settings_check(func_name): Value cannot be empty or null.'
            )

        if not isinstance(settings, dict):
            raise TypeError(
                '{0}(settings): Expected <dict>. Got "{1}" instead.'.format(
                    func_name, type(settings))
            )

        if not settings:
            raise ValueError(
                '_{0}(settings): Settings cannot be empty'.format(func_name)
            )

        if settings.keys() != self.defaults().keys():
            raise KeyError(
                '{0}(settings): Invalid settings detected.'.format(func_name)
            )

        return True

    def test_process_profile_dictionary(self, old_dict, file_list=None, new_dict=None):
        if new_dict is None:
            new_dict = {}

        if file_list is None:
            file_list = []

        for k, v in old_dict.items():
            if k.endswith('.py'):
                file_list.append(k+'.csv')

            if not isinstance(v, dict):
                new_dict[k] = v
            else:
                self._process_profile_dictionary(v, new_dict)

        return new_dict

    @staticmethod
    def test_float_or_int_tester(string_to_test, verbose=False):
        # tests whether item is a string, float or int, and returns the result as a converted item
        # pylint: disable=too-many-branches
        if verbose:
            print('Verbose: Enter _float_or_int_tester()')

        if not isinstance(string_to_test, str):
            return string_to_test

        two_nums = []
        if '/' in string_to_test:
            two_nums.append(string_to_test.split('/'))

        if '.' not in string_to_test:
            try:
                if two_nums and (int(two_nums[0]) > int(two_nums[1])):
                    string_to_test = int(two_nums[0])
                elif two_nums and (int(two_nums[0]) < int(two_nums[1])):
                    string_to_test = int(two_nums[1])
                else:
                    string_to_test = int(string_to_test)
                return string_to_test
            except ValueError as v_err:
                if verbose:
                    print(v_err)
            except TypeError as t_err:
                if verbose:
                    print(t_err)

        try:
            string_to_test = float(string_to_test)
            return string_to_test
        except ValueError as err:
            if verbose:
                print(err)
            return string_to_test

    def test_cprofile_field_structure_tester(self, item_to_test: list, verbose=False):
        # Accepts a list of objects and tests whether their type has the pattern
        # int, float, float, float, float, string
        # returns a tuple of matching strings
        # pylint: disable=too-many-branches

        if verbose:
            print('Verbose: Enter cprofile_field_structure_tester with item_to_test={}'
                  .format(item_to_test))

        if not isinstance(item_to_test, list):
            if verbose:
                print('Error: {} is not of type <list>. Got type <{}> instead'
                      .format(item_to_test, type(item_to_test)))
            return []

        item_list_length = len(item_to_test)

        type_list = []
        for item in item_to_test:
            type_list.append(type(item))

        if verbose:
            print('Verbose: type_list = {}'.format(type_list))
            print('Verbose: item_list_length = {}'.format(item_list_length))

        structure = {
            0: int,
            1: float,
            2: float,
            3: float,
            4: float,
            5: str,
        }

        test_tuple = ()
        results_tuple = ()
        comparison = (int, float, float, float, float, str)

        if len(item_to_test) != len(structure.values()):
            if verbose:
                print('Verbose: Exit cprofile_field_structure_tester length {} != {}'
                      .format(len(item_to_test), len(structure.values())))
            return False

        for position, item in enumerate(item_to_test):
            if isinstance(self._float_or_int_tester(item, verbose=verbose), structure[position]):
                test_tuple += (type(structure[position](item)),)
                results_tuple += (structure[position](item),)

        for position, item in enumerate(test_tuple):
            if item == comparison[position]:
                continue
            else:
                if verbose:
                    print('Verbose: Exit cprofile_field_structure_tester as False')
                return False

        if verbose:
            print('Verbose: Exit cprofile_field_structure_tester with results_tuple: {}'
                  .format(results_tuple))

        return results_tuple

    def test_help_args_checker(self, settings):
        # Checks the settings for -h and --help and if they are True prints help_messsage
        self._settings_check(func_name='_help_arg_checker', settings=settings)

        if settings['-h'] is True or settings['--help'] is True:
            return "Help!"

    def test_reset_settings_for_help(self):
        # provides settings with help information
        new_settings = self.defaults()
        new_settings['--help'] = True
        new_settings['-h'] = True

        return new_settings

    @staticmethod
    def test_cprofile_bytes_to_string(bytes_objects):
        # Takes list of bytes objects, converts to string and returns the list of strings
        return [str(i).replace('b\'', '').replace('b"', '') for i in bytes_objects]

    def test_create_cprofile_dictionary(self, cprofile_list, file, verbose=False):
        # Takes list of strings and returns a dictionary
        _, file_name = path.split(file)
        data_dict = {
            file_name: {
                'total_function_calls': None,
                'total_primitive_calls': None,
                'total_function_call_seconds': None,
            }
        }

        func_calls_regex = r"\d+ \w+ calls"
        c_func_calls_regex = re.compile(func_calls_regex)
        stats_regex = r"([\d+ ])+"
        func_file_list = []
        line_no_list = []
        func_name_list = []
        n_calls_list = []
        tot_time_list = []
        tot_time_percall_list = []
        cum_time_list = []
        cum_time_per_call = []

        for i in cprofile_list:
            if re.findall(c_func_calls_regex, i):
                if 'function' in i.split():
                    data_dict[file_name]['total_function_calls'] = float(i.split()[0])
                    data_dict[file_name]['total_primitive_calls'] = 0.0
                    data_dict[file_name]['total_function_call_seconds'] = float(i.split()[-2])
                if 'function' and 'primitive' in i.split():
                    data_dict[file_name]['total_primitive_calls'] = float(
                        i.split()[3].replace('(', ''))
            if re.findall(stats_regex, i):
                i_tuple = self._cprofile_field_structure_tester(i.split(), verbose=verbose)
                if i_tuple:
                    func_file_list.append(str(i_tuple[5]).split(':')[0])
                    line_no_list.append(int(str(i_tuple[5]).split(':')[1].split('(')[0]))
                    func_name_list.append(str(i_tuple[5]).split('(')[1].replace(')\'', ''))
                    n_calls_list.append(i_tuple[0])
                    tot_time_list.append(i_tuple[1])
                    tot_time_percall_list.append(i_tuple[2])
                    cum_time_list.append(i_tuple[3])
                    cum_time_per_call.append(i_tuple[4])

        for i in cprofile_list:
            if re.findall(stats_regex, i):
                i_tuple = self._cprofile_field_structure_tester(i.split(), verbose=verbose)
                if i_tuple:
                    data_dict[file_name]['function_stats'] = {
                        'func_file': func_file_list,
                        'func_file_line_no': line_no_list,
                        'func_name': func_name_list,
                        'ncalls': n_calls_list,
                        'tottime': tot_time_list,
                        'tottime_percall': tot_time_percall_list,
                        'cumtime': cum_time_list,
                        'cumtime_percall': cum_time_per_call,
                    }
        return data_dict

    def test_cprofile_file_data(self, cprofile_dict):
        """Returns a list of function_name, function_data tuples

        function_name is a string, and function_data is a list of dictionaries
        that will turn into lines in the csv writer.
        """
        output = []
        for file_name, dict_value in cprofile_dict.items():
            file_dictionaries = []

            function_stats = dict_value['function_stats']
            # The length of one of the lists in the function_stats dictionary
            len_of_stat = len(function_stats[list(function_stats)[0]])

            d = {total: dict_value[total] for total in ['total_function_calls',
                                                        'total_primitive_calls',
                                                        'total_function_call_seconds']}
            for index in range(len_of_stat):
                for stat in ['func_file', 'func_file_line_no', 'func_name', 'ncalls', 'tottime',
                             'tottime_percall', 'cumtime', 'tottime_percall', 'cumtime',
                             'cumtime_percall']:
                    d[stat] = function_stats[stat][index]

                if index == 1:
                    d['total_function_calls'] = d['total_primitive_calls'] = \
                        d['total_primitive_calls'] = None

                file_dictionaries.append(d.copy())
            output.append((file_name, file_dictionaries))
        return output

    @staticmethod
    def test_run_cprofile(file_name, settings):
        # Test run cprofile
        #pylint: disable=bad-continuation,anomalous-backslash-in-string
        if settings['-v'] is True:
            print('Verbose: Enter test_run_cprofile()')

        if isinstance(file_name, str):
            if settings['-v'] is True:
                print('Verbose: Exit test_run_cprofile()')

            return [b'ALLUSERSPROFILE: C:\\ProgramData',
                    b'APPDATA: C:\\Users\\rscih\\AppData\\Roaming',
                    b'COMMONPROGRAMFILES: C:\\Program Files (x86)\\Common Files',
                    b'COMMONPROGRAMFILES(X86): C:\\Program Files (x86)\\Common Files',
                    b'COMMONPROGRAMW6432: C:\\Program Files\\Common Files',
                    b'COMPUTERNAME: SFUT-2PTVMH2', b'COMSPEC: C:\\WINDOWS\\system32\\cmd.exe',
                    b'DEFLOGDIR: C:\\ProgramData\\McAfee\\Endpoint Security\\Logs',
                    b'DRIVERDATA: C:\\Windows\\System32\\Drivers\\DriverData', b'HOMEDRIVE: H:',
                    b'HOMEPATH: \\', b'HOMESHARE: \\\\ebihome-ro-02\\rscih',
                    b'IDE_PROJECT_ROOTS: C:/Users/rscih/PycharmProjects/EUA-4395-Write-a-Standa\
lone-Performance-Testing-Utility-in-Python', b'IPYTHONENABLE: True', b'LIBRARY_ROOTS: C:/APPS/UADEV\
/py_2.1.104/py;C:/Users/rscih/AppData/Local/Programs/Python/Python36-32/DLLs;C:/Users/rscih/AppDa\
ta/Local/Programs/Python/Python36-32/Lib;C:/Users/rscih/AppData/Local/Programs/Python/Python36-32;\
C:/Users/rscih/AppData/Local/Programs/Python/Python36-32/Lib/site-packages;C:/Users/rscih/.PyCharmC\
E2017.2/system/python_stubs/1790106858;C:/Program Files (x86)/JetBrains/PyCharm Community Edition \
2017.2.4/helpers/python-skeletons;C:/Program Files (x86)/JetBrains/PyCharm Community Edition 2017.2\
.4/helpers/typeshed/stdlib/3.6;C:/Program Files (x86)/JetBrains/PyCharm Community Edition 2017.2.4/\
helpers/typeshed/stdlib/3.5;C:/Program Files (x86)/JetBrains/PyCharm Community Edition 2017.2.4/hel\
pers/typeshed/stdlib/3.4;C:/Program Files (x86)/JetBrains/PyCharm Community Edition 2017.2.4/helper\
s/typeshed/stdlib/3.3;C:/Program Files (x86)/JetBrains/PyCharm Community Edition 2017.2.4/helpers/t\
ypeshed/stdlib/3;C:/Program Files (x86)/JetBrains/PyCharm Community Edition 2017.2.4/helpers/typesh\
ed/stdlib/2and3;C:/Program Files (x86)/JetBrains/PyCharm Community Edition 2017.2.4/helpers/typeshe\
d/third_party/3;C:/Program Files (x86)/JetBrains/PyCharm Community Edition 2017.2.4/helpers/typeshe\
d/third_party/2and3',
                        b'LOCALAPPDATA: C:\\Users\\rscih\\AppData\\Local',
                        b'LOGONSERVER: \\\\A0775-TRS1607-D', b'NUMBER_OF_PROCESSORS: 8',
                        b'ONEDRIVE: C:\\Users\\rscih\\OneDrive - Allstate',
                        b'ORACLE_HOME: \\oracle\\product\\12.1.0.2_32b', b'OS: Windows_NT',
                        b'PATH:', b'\t\t\\APPS\\UADEV\\py_2.1.104\\bin',
                        b'\t\t\\oracle\\product\\12.1.0.2_32b\\bin',
                        b'\t\t\\APPS\\UADEV\\py_2.1.104\\bin',
                        b'\t\t\\oracle\\product\\12.1.0.2_32b\\bin',
                        b'\t\tC:\\APPS\\UADEV\\py_2.1.104\\bin',
                        b'\t\tC:\\oracle\\product\\12.1.0.2_32b\\bin',
                        b'\t\tC:\\Program Files (x86)\\Common Files\\Oracle\\Java\\javapath',
                        b'\t\tc:\\oracle\\product\\12.1.0.2_32b\\bin', b'\t\tC:\\WINDOWS\\system32',
                        b'\t\tC:\\WINDOWS', b'\t\tC:\\WINDOWS\\System32\\Wbem',
                        b'\t\tC:\\WINDOWS\\System32\\WindowsPowerShell\\v1.0\\',
                        b'\t\tC:\\Program Files (x86)\\PuTTY\\',
                        b'\t\tC:\\WINDOWS\\System32\\OpenSSH\\',
                        b'\t\tC:\\Users\\rscih\\AppData\\Local\\Programs\\Python\\Python36-32\\Scri\
pts\\', b'\t\tC:\\Users\\rscih\\AppData\\Local\\Programs\\Python\\Python36-32\\', b'\t\tC:\\User\
s\\rscih\\AppData\\Local\\Programs\\Python\\Launcher\\',
                        b'\t\tC:\\Users\\rscih\\AppData\\Local\\Microsoft\\WindowsApps',
                        b'\t\tC:\\Users\\rscih\\AppData\\Local\\Programs\\Git\\cmd', b'\t\t',
                        b'PATHEXT: .COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC',
                        b'PROCESSOR_ARCHITECTURE: x86', b'PROCESSOR_ARCHITEW6432: AMD64',
                        b'PROCESSOR_IDENTIFIER: Intel64 Family 6 Model 158 Stepping 9, GenuineInte\
l',
                        b'PROCESSOR_LEVEL: 6', b'PROCESSOR_REVISION: 9e09',
                        b'PROGRAMDATA: C:\\ProgramData', b'PROGRAMFILES: C:\\Program Files (x86)',
                        b'PROGRAMFILES(X86): C:\\Program Files (x86)',
                        b'PROGRAMW6432: C:\\Program Files', b'PROMPT: $P$G',
                        b'PSMODULEPATH: C:\\Program Files\\WindowsPowerShell\\Modules;C:\\WINDOWS\\\
system32\\WindowsPowerShell\\v1.0\\Modules', b'PUBLIC: C:\\Users\\Public', b'PYCHARM_HOSTED: 1',
                        b'PYTHONDONTWRITEBYTECODE: 1', b'PYTHONIOENCODING: UTF-8',
                        b'PYTHONPATH: \\APPS\\UADEV\\py_2.1.104py', b'PYTHONUNBUFFERED: 1',
                        b'PYTHON_IDE_LOCATION: \\Program Files (x86)\\JetBrains\\PyCharm Community \
Edition 2017.2.4\\bin\\pycharm64.exe', b'SAVEDHOMEDRIVE: \\\\ebihome-ro-02\\rscih',
                        b'SESSIONNAME: Console', b'SYSTEMDRIVE: C:', b'SYSTEMROOT: C:\\WINDOWS',
                        b'TEMP: C:\\Users\\rscih\\AppData\\Local\\Temp',
                        b'TENFOLD_OPTIONS: TFPX_dev1.ini',
                        b'TENFOLD_ROOT: \\APPS\\UADEV\\py_2.1.104',
                        b'TMP: C:\\Users\\rscih\\AppData\\Local\\Temp',
                        b'UATDATA: C:\\Windows\\CCM\\UATData\\D9F8C395-CAB8-491d-B8AC-179A1FE1BE77',
                        b'USERDNSDOMAIN: AD.ALLSTATE.COM', b'USERDOMAIN: AD',
                        b'USERDOMAIN_ROAMINGPROFILE: AD', b'USERNAME: rscih',
                        b'USERPROFILE: C:\\Users\\rscih', b'WINDIR: C:\\WINDOWS', b'',
                        b'         1074 function calls in 0.003 seconds', b'',
                        b'   Ordered by: cumulative time', b'',
                        b'   ncalls  tottime  percall  cumtime  percall filename:lineno(function)',
                        b'        1    0.000    0.000    0.003    0.003 {built-in method builtins.e\
xec}', b'        1    0.000    0.000    0.003    0.003 py_environment.py:1(<module>)',
                        b'        1    0.000    0.000    0.003    0.003 py_environment.py:89(mai\
n)', b'        1    0.000    0.000    0.002    0.002 py_environment.py:52(import_py)',
                        b'        1    0.000    0.000    0.002    0.002 <frozen importlib._bootstra\
p>:966(_find_and_load)', b'        1    0.000    0.000    0.002    0.002 <frozen importlib._bootstr\
ap>:936(_find_and_load_unlocked)',
                        b'        1    0.000    0.000    0.002    0.002 <frozen importlib._bootstra\
p>:870(_find_spec)',
                        b'        1    0.000    0.000    0.002    0.002 <frozen importlib._bootstra\
p_external>:1149(find_spec)', b'        1    0.000    0.000    0.002    0.002 <frozen importlib._bo\
otstrap_external>:1117(_get_spec)', b'        6    0.000    0.000    0.001    0.000 <frozen importl\
ib._bootstrap_external>:1233(find_spec)', b'        7    0.000    0.000    0.001    0.000 <frozen i\
mportlib._bootstrap_external>:75(_path_stat)',
                        b'        7    0.001    0.000    0.001    0.000 {built-in method nt.stat}',
                        b'        1    0.000    0.000    0.001    0.001 py_environment.py:21(py\
_env_setup)',
                        b'        1    0.000    0.000    0.000    0.000 py_environment.py:72(envi\
ronment_vars)',
                        b'       57    0.000    0.000    0.000    0.000 _collections_abc.py:742(__i\
ter__)', b'        8    0.000    0.000    0.000    0.000 <frozen importlib._bootstrap_external>:108\
0(_path_importer_cache)', b'        1    0.000    0.000    0.000    0.000 {built-in method nt.chdir\
}', b'        1    0.000    0.000    0.000    0.000 <frozen importlib._bootstrap_external>:1067(_pa\
th_hooks)', b'        1    0.000    0.000    0.000    0.000 <frozen importlib._bootstrap_external>:\
1281(_fill_cache)', b'        1    0.000    0.000    0.000    0.000 {built-in method nt.listdir}',
                        b'        6    0.000    0.000    0.000    0.000 os.py:672(__setitem__)',
                        b'       61    0.000    0.000    0.000    0.000 os.py:664(__getitem__)',
                        b'        1    0.000    0.000    0.000    0.000 pydevd_file_utils.py:386(ge\
t_abs_path_real_path_and_base_from_frame)',
                        b'        1    0.000    0.000    0.000    0.000 <frozen importlib._bootstra\
p_external>:1322(path_hook_for_FileFinder)', b'        1    0.000    0.000    0.000    0.000 pydevd\
_file_utils.py:375(get_abs_path_real_path_and_base_from_file)', b'       67    0.000    0.000    0.\
000    0.000 os.py:734(encodekey)', b'        1    0.000    0.000    0.000    0.000 pydevd_file_uti\
ls.py:155(_NormPaths)', b'        6    0.000    0.000    0.000    0.000 {built-in method nt.putenv\
}',
                        b'        1    0.000    0.000    0.000    0.000 <frozen importlib._bootstra\
p_external>:99(_path_isdir)', b'        1    0.000    0.000    0.000    0.000 <frozen importlib._bo\
otstrap_external>:85(_path_is_mode_type)', b'        2    0.000    0.000    0.000    0.000 pydevd_f\
ile_utils.py:166(_NormPath)', b'       30    0.000    0.000    0.000    0.000 <frozen importlib._bo\
otstrap_external>:57(_path_join)', b'        2    0.000    0.000    0.000    0.000 ntpath.py:538(ab\
spath)',
                        b'       73    0.000    0.000    0.000    0.000 os.py:728(check_str)',
                        b"       79    0.000    0.000    0.000    0.000 {method 'format' of 'str' o\
bjects}", b'        2    0.000    0.000    0.000    0.000 ntpath.py:471(normpath)',
                        b'       38    0.000    0.000    0.000    0.000 threading.py:1230(current_t\
hread)', b'        2    0.000    0.000    0.000    0.000 pydevd_file_utils.py:95(norm_case)',
                        b'        1    0.000    0.000    0.000    0.000 {built-in method builtins.p\
rint}', b'       30    0.000    0.000    0.000    0.000 <frozen importlib._bootstrap_external>:59(<\
listcomp>)',
                        b'        1    0.000    0.000    0.000    0.000 <frozen importlib._bootstra\
p>:147(__enter__)',
                        b'       89    0.000    0.000    0.000    0.000 {built-in method builtins.i\
sinstance}', b'       57    0.000    0.000    0.000    0.000 os.py:687(__iter__)',
                        b'        1    0.000    0.000    0.000    0.000 <frozen importlib._bootstra\
p_external>:1196(__init__)',
                        b'        1    0.000    0.000    0.000    0.000 ntpath.py:233(basename)',
                        b'        2    0.000    0.000    0.000    0.000 _pydev_filesystem_encoding.\
py:29(getfilesystemencoding)',
                        b'        1    0.000    0.000    0.000    0.000 <frozen importlib._bootstra\
p>:157(_get_module_lock)',
                        b'        1    0.000    0.000    0.000    0.000 ntpath.py:199(split)',
                        b'        3    0.000    0.000    0.000    0.000 ntpath.py:121(splitdrive)',
                        b'       30    0.000    0.000    0.000    0.000 <frozen importlib._bootstra\
p>:222(_verbose_message)',
                        b"       61    0.000    0.000    0.000    0.000 {method 'rstrip' of 'str' o\
bjects}", b"        3    0.000    0.000    0.000    0.000 {method 'extend' of 'list' objects}",
                        b"       67    0.000    0.000    0.000    0.000 {method 'upper' of 'str' ob\
jects}", b'        1    0.000    0.000    0.000    0.000 _collections_abc.py:676(items)',
                        b"       38    0.000    0.000    0.000    0.000 {method 'join' of 'str' obj\
ects}", b'       12    0.000    0.000    0.000    0.000 {built-in method builtins.hasattr}',
                        b'        1    0.000    0.000    0.000    0.000 <frozen importlib._bootstra\
p>:58(__init__)', b'        1    0.000    0.000    0.000    0.000 <frozen importlib._bootstrap>:151\
(__exit__)',
                        b'        1    0.000    0.000    0.000    0.000 <frozen importlib._bootstra\
p>:707(find_spec)', b'        2    0.000    0.000    0.000    0.000 ntpath.py:43(normcase)',
                        b'        1    0.000    0.000    0.000    0.000 <frozen importlib._bootstra\
p>:78(acquire)', b'        2    0.000    0.000    0.000    0.000 {built-in method _thread.allocate_\
lock}',
                        b'        1    0.000    0.000    0.000    0.000 <frozen importlib._bootstra\
p_external>:1310(<setcomp>)',
                        b'       40    0.000    0.000    0.000    0.000 {built-in method _thread.ge\
t_ident}', b"        3    0.000    0.000    0.000    0.000 {method 'split' of 'str' objects}",
                        b'        2    0.000    0.000    0.000    0.000 {built-in method nt._getful\
lpathname}',
                        b'        6    0.000    0.000    0.000    0.000 <frozen importlib._bootstra\
p_external>:37(_relax_case)',
                        b'        1    0.000    0.000    0.000    0.000 <frozen importlib._bootstra\
p>:103(release)',
                        b'        2    0.000    0.000    0.000    0.000 <frozen importlib._bootstra\
p>:997(_handle_fromlist)',
                        b"        7    0.000    0.000    0.000    0.000 {method 'startswith' of 'st\
r' objects}",
                        b'        1    0.000    0.000    0.000    0.000 {built-in method _imp.is_bu\
iltin}',
                        b'        2    0.000    0.000    0.000    0.000 _pydev_filesystem_encoding.\
py:4(__getfilesystemencoding)',
                        b'       10    0.000    0.000    0.000    0.000 pydevd_comm.py:254(get_glob\
al_debugger)',
                        b'        1    0.000    0.000    0.000    0.000 <frozen importlib._bootstra\
p>:176(cb)',
                        b'        8    0.000    0.000    0.000    0.000 <frozen importlib._bootstra\
p_external>:1202(<genexpr>)',
                        b"       14    0.000    0.000    0.000    0.000 {method 'lower' of 'str' ob\
jects}",
                        b'        1    0.000    0.000    0.000    0.000 <frozen importlib._bootstra\
p>:780(find_spec)',
                        b'        3    0.000    0.000    0.000    0.000 <frozen importlib._bootstra\
p>:847(__exit__)', b"        7    0.000    0.000    0.000    0.000 {method 'replace' of 'str' objec\
ts}", b"        9    0.000    0.000    0.000    0.000 {method 'partition' of 'str' objects}",
                        b'        3    0.000    0.000    0.000    0.000 <frozen importlib._bootstra\
p>:843(__enter__)',
                        b"        4    0.000    0.000    0.000    0.000 {method 'find' of 'str' obj\
ects}", b"        7    0.000    0.000    0.000    0.000 {method 'rpartition' of 'str' objects}",
                        b'        1    0.000    0.000    0.000    0.000 <frozen importlib._bootstra\
p>:143(__init__)', b'        1    0.000    0.000    0.000    0.000 <frozen importlib._bootstrap>:36\
9(__init__)', b'       10    0.000    0.000    0.000    0.000 {built-in method nt.fspath}',
                        b"        9    0.000    0.000    0.000    0.000 {method 'add' of 'set' obje\
cts}",
                        b'        1    0.000    0.000    0.000    0.000 _collections_abc.py:698(__i\
nit__)', b"        2    0.000    0.000    0.000    0.000 {method 'encode' of 'str' objects}",
                        b"        2    0.000    0.000    0.000    0.000 {method 'lstrip' of 'str' o\
bjects}", b'       16    0.000    0.000    0.000    0.000 {built-in method builtins.len}',
                        b'        5    0.000    0.000    0.000    0.000 {built-in method _imp.relea\
se_lock}', b'        1    0.000    0.000    0.000    0.000 ntpath.py:33(_get_bothseps)', b'        \
1    0.000    0.000    0.000    0.000 {built-in method nt.getcwd}',
                        b"        2    0.000    0.000    0.000    0.000 {method 'get' of 'dict' obj\
ects}", b"        1    0.000    0.000    0.000    0.000 {method 'endswith' of 'str' objects}",
                        b'        5    0.000    0.000    0.000    0.000 {built-in method _imp.acqui\
re_lock}', b'        1    0.000    0.000    0.000    0.000 {built-in method _imp.is_frozen}',
                        b'        2    0.000    0.000    0.000    0.000 {built-in method sys.getfil\
esystemencoding}',
                        b"        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lspr\
of.Pr\ofiler' objects}", b'', b'', b''], file_name

    @staticmethod
    def test_args_or_argv(args=None):
        # Checks for argv or otherwise takes a list
        if not isinstance(args, list) and len(argv) == 1:
            raise TypeError(
                '_args_or_argv(args): Expected <list>. Got {} instead. sys.argv = {}'.format(
                    type(args), argv))
        elif (len(argv) == 1 and len(args) != 0) and args[0] == argv[0]:
            return argv[1:], 'argv'
        elif args:
            return args, 'args'
        else:
            raise ValueError(
                '_args_or_argv(args): <list> or <sys.argv> cannot be empty.'
            )

    def test_check_for_other_arg(self, arg_list, base_arg_1, base_arg_2, verbose=False):
        # Checks if there is another switch in the arg_list
        # If so, it returns the help settings

        if verbose:
            print('Enter test_check_for_other_arg()')

        if base_arg_1 in arg_list or base_arg_2 in arg_list:
            other_arg = []
            for position, switch in enumerate(self.switches):
                if switch == base_arg_1 or switch == base_arg_2:
                    continue
                elif switch in arg_list:
                    other_arg.append(True)
            if True not in other_arg:
                if verbose:
                    print('Verbose: Invalid setting: "{}" or "{}" requires another switch'.format(
                        base_arg_1, base_arg_2))
                    print('Verbose: Exit test_check_for_other_arg()')
                return self.test_reset_settings_for_help()

    def test_arg_parser(self, arg_list=None, flag=None, verbose=False):
        # pylint: disable=too-many-branches
        """
        Processes input from command line or list
        :param arg_list: <list> expected. None by default.
        :param flag: <string> or <None> (default). If <string> 'args' or 'argv' expected.
        :param verbose: True for extra print statements.
        :return: dictionary of configured settings
        """

        if verbose:
            print('Verbose: Enter test_arg_parser()')

        if not isinstance(arg_list, list):
            raise TypeError('test_arg_parser() requires a list')

        if not isinstance(flag, str):
            raise TypeError(
                'test_arg_parser(flag): Expected <string>. Got {0} instead.'.format(type(flag))
            )

        if flag not in ('argv', 'args'):
            raise ValueError(
                'test_arg_parser(flag): Expected "args" or "argv". Got {} instead'.format(flag)
            )

        args_dict = self.defaults()

        for index, item in enumerate(arg_list):
            if item.lower() in self.switches:
                arg_list[index] = item.lower()

        valid = []
        for item in self.switches:
            if item not in arg_list:
                valid.append(False)
            else:
                valid.append(True)

        if True not in valid:
            if verbose:
                print('Verbose: Exit test_arg_parser()')
            raise ValueError('test_arg_parser(arg_list): No valid arguments detected')
        elif verbose:
            print('Verbose: test_arg_parser(arg_list): Contains valid arguments')

        # Sanitize argument list to prevent process when invalid settings are detected
        if '-h' in arg_list or '--help' in arg_list:
            if verbose:
                print('Verbose: Help Detected: Returning settings with only Help set to True')
                print('Verbose: Exit test_arg_parser()')
            return self.test_reset_settings_for_help()

        if '-r' in arg_list and '-w' in arg_list:
            if verbose:
                print('Verbose: Invalid settings: "-w" and "-r" cannot be together')
                print('Verbose: Exit test_arg_parser()')
            return self.test_reset_settings_for_help()

        if '--recurse' in arg_list and '-w' in arg_list:
            if verbose:
                print('Verbose: Invalid settings: "-w" and "--recurse" cannot be together')
                print('Verbose: Exit test_arg_parser()')
            return self.test_reset_settings_for_help()

        if '-r' in arg_list and '--working-dir' in arg_list:
            if verbose:
                print('Verbose: Invalid settings: "--working-dir" and "-r" cannot be together')
                print('Verbose: Exit test_arg_parser()')
            return self.test_reset_settings_for_help()

        if self.test_reset_settings_for_help() == self.test_check_for_other_arg(
                arg_list=arg_list, base_arg_1='-v', base_arg_2='--verbose',  verbose=verbose):
            return self.test_reset_settings_for_help()

        if self.test_reset_settings_for_help() == self.test_check_for_other_arg(
                arg_list=arg_list, base_arg_1='-d', base_arg_2='--directory',  verbose=verbose):
            return self.test_reset_settings_for_help()

        # pylint: disable=consider-iterating-dictionary
        for key in args_dict.keys():
            if key in arg_list:
                if key == '-d':
                    if verbose:
                        print('Verbose: -d found')
                    directory_index = arg_list.index(key)
                    if arg_list.index(arg_list[-1]) < directory_index+1:
                        raise SyntaxError('-d requires a space and path name')
                    args_dict[key] = arg_list[directory_index+1]
                    args_dict['--directory'] = arg_list[directory_index+1]
                elif key == '--directory':
                    if verbose:
                        print('Verbose: --directory found')
                    directory_index = arg_list.index(key)
                    if arg_list.index(arg_list[-1]) < directory_index+1:
                        raise SyntaxError('--directory requires a space and path name')
                    args_dict[key] = arg_list[directory_index+1]
                    args_dict['-d'] = arg_list[directory_index+1]
                elif key == '-f':
                    if verbose:
                        print('Verbose: -f found')
                    file_index = arg_list.index(key)
                    if arg_list.index(arg_list[-1]) < file_index+1:
                        raise SyntaxError('-f requires a space and file path')
                    args_dict[key] = arg_list[file_index+1]
                    args_dict['--file'] = arg_list[file_index+1]
                elif key == '--file':
                    if verbose:
                        print('Verbose: --file found')
                    file_index = arg_list.index(key)
                    if arg_list.index(arg_list[-1]) < file_index+1:
                        raise SyntaxError('--file requires a space and file path')
                    args_dict[key] = arg_list[file_index+1]
                    args_dict['-f'] = arg_list[file_index+1]
                elif key == '-w':
                    if verbose:
                        print('Verbose: -w found')
                    args_dict[key] = True
                    args_dict['--working-dir'] = True
                elif key == '--working-dir':
                    if verbose:
                        print('Verbose: --working-dir found')
                    args_dict[key] = True
                    args_dict['-w'] = True
                elif key == '-r':
                    if verbose:
                        print('Verbose: -r found')
                    args_dict[key] = True
                    args_dict['--recurse'] = True
                elif key == '--recurse':
                    if verbose:
                        print('Verbose: --recurse found')
                    args_dict[key] = True
                    args_dict['-r'] = True
                elif key == '-v':
                    if verbose:
                        print('Verbose: -v found')
                    args_dict[key] = True
                    args_dict['--verbose'] = True
                elif key == '--verbose':
                    if verbose:
                        print('Verbose: --verbose found')
                    args_dict[key] = True
                    args_dict['-v'] = True

        if verbose:
            print('Verbose: Exit test_arg_parser()')

        return args_dict

    def test_set_verbosity(self, settings):
        # sets the verbose level to True or False
        self._settings_check(func_name='_set_verbosity', settings=settings)
        if settings['-v'] is True or settings['--verbose'] is True:
            return True
        else:
            return False

    def test_change_directories(self, settings):
        # If --directory or -d is True, changes to that directory
        self._settings_check(func_name='_change_directories', settings=settings)

        if settings['-d'] is not None:
            chdir(settings['-d'])
            return True
        elif settings['--directory'] is not None:
            chdir(settings['--directory'])
            return True
        elif settings['-d'] is None and settings['--directory'] is None:
            if settings['-v'] is True or settings['--verbose'] is True:
                print('Verbose: _change_directories: Directory blank. Using working directory.')
            working_directory, _ = path.split(argv[0])
            chdir(working_directory)

    def test_run_performance_tests(self, arguments=None, verbose=False):
        """
        Main performance test function. Runs various helper functions to extract output,
        parse the data, and return data in a data structure for analysis and reporting
        :param arguments: <list> or <sys.argv> type. Default is sys.argv. Allows using list
                            for unit testing or using this as a module in another application.
        :param verbose: True or False
        :return: dictionary with values as list of tuples
        """
        start = time()

        if verbose:
            print('Verbose: Enter run_performance_tests()')

        working_dir, _ = path.split(argv[0])
        chdir(working_dir)

        args, flag = self.test_args_or_argv(args=arguments)
        settings = self.test_arg_parser(arg_list=args, flag=flag, verbose=verbose)
        verbose = self.test_set_verbosity(settings=settings)
        self.test_change_directories(settings=settings)

        if not args and flag == 'args':
            print('test_arg_parser(arg_list): List cannot be empty.')
            return self.test_reset_settings_for_help()

        if len(argv) == 1 and flag == 'argv':
            print('test_arg_parser(arg_list): Command line args cannot not be empty')
            return self.test_reset_settings_for_help()

        print('Settings from test_run_performance_tests: {}'.format(settings))
        files = self.test_get_file_list(settings=settings)
        print('files: {}'.format(files))

        if verbose:
            print('Verbose: files: {}'.format(files))

        master_dict = {}
        for p, i in enumerate(files):
            print('Processing file: {}'.format(i))
            cprofile_bytes_list, file_name = self.test_run_cprofile(file_name=i, settings=settings)
            cprofile_string_list = self.test_cprofile_bytes_to_string(cprofile_bytes_list)
            master_dict.update(self.test_create_cprofile_dictionary(
                cprofile_list=cprofile_string_list, file=file_name, verbose=verbose))
        if verbose:
            print(self.timer(block_name='run_performance_tests', start=start, verbose=verbose))
            print('Verbose: Exit run_performance_tests()')

        return master_dict

    def test_prep_for_cprofile_list_of_dicts_to_csv(self, test_file_dict_tuples):
        # preps data for cprofile_transform_list_of_dicts
        # sends list of dictionary lines to test_cprofile_list_of_dicts_to_csv
        # For testing purposes, returns tuple (output_file_names, list_of_dictionary_lines_list)
        output_file_names = []
        list_of_dictionary_lines_list = []
        for file_data in test_file_dict_tuples:
            list_of_dictionary_lines = file_data[1]
            file_name = file_data[0].split('.')[0] + '-' + datetime.datetime.today().strftime(
                '%Y-%m-%d-%H-%M-%S') + '.csv'

            list_of_dictionary_lines_list.append(list_of_dictionary_lines)
            output_file_names.append(file_name)

            self.test_cprofile_list_of_dicts_to_csv(list_of_dictionary_lines, file_name)

        return output_file_names, list_of_dictionary_lines_list

    def test_cprofile_list_of_dicts_to_csv(self, dict_lines: list, file_name: str):
        """
        Writes a list of dictionaries to a csv file using keys as columns and
        values as rows
        :param: dict_lines: <list> list of dictionaries
        :param: file_name: <string> name of the csv file
        """

        if isinstance(dict_lines, list) and dict_lines:
            csv_columns = dict_lines[0].keys()
            csv_rows = []
            resulting_list = []
            for dictionary in dict_lines:
                csv_rows.append(dictionary)

            resulting_list.append([csv_columns, csv_rows])

            return resulting_list
        else:
            raise ValueError("Requires a nonempty list of dictionaries")


def main():
    main_section = PyProfiler()
    main_section.verbose = False
    results = main_section.run_performance_tests(verbose=main_section.verbose)

    script_path, _ = path.split(argv[0])
    chdir(script_path)

    file_dict_tuples = main_section.cprofile_file_data(results)
    main_section.prep_for_cprofile_list_of_dicts_to_csv(test_file_dict_tuples=file_dict_tuples)


if __name__ == "__main__":
    main()
