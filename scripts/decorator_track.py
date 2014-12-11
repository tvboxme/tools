import pickle
from functools import wraps
import sys,types
import shutil
n = 0
indent = 0
import_name = 'decorate_.py'
list = []
def print_name(print_arg=True, print_arg_once=True, print_once=False):
    """ general decorator"""
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            global n, last_func,indent
            indent+=1
            simple_item = func.__module__+'.'+func.__name__
            if print_arg:
                new_item= func.__module__+'.'+func.__name__+':'+str(args)[:100]+' '+str(kwargs)[:100]
                if print_arg_once:
                    if simple_item in list:
                        new_item = simple_item
                    else:
                        list.append(simple_item)
            else:
                new_item = simple_item
            if print_once and new_item in list:
                pass
            else:
                print '*'*indent,'Calling',new_item
                list.append(new_item)
            #this will print only if there is exception
            #f = sys.exc_info()[2].tb_frame.f_back
            #print f.f_code
            result = func(*args, **kwargs)
            #print '*'*indent,'Ret of  %s: ' % (func.__module__+'.'+func.__name__), result
            if indent == 1:
                print '\n'
            indent -=1
            return result
        return wrapper
    return decorate

import os,re,shutil
def remove_decorator(source_dir=None):
    # source_dir='/home/jessiex/git/stress/scripts'
    if source_dir == None:
        source_dir = os.getcwd()
    for (top, folders, files) in os.walk(source_dir):

        print (top, folders, files)
        for file in files:
            filepath = os.path.join(top,file)
            if file.endswith('.d_bak'):
                shutil.copy(filepath,filepath[:-1*len('.d_bak')])

def add_decorator(source_dir=None, print_arg=True, print_arg_once=True, print_once=False):
    # source_dir='/home/jessiex/git/stress/scripts'
    if source_dir == None:
        source_dir = os.getcwd()
    for (top, folders, files) in os.walk(source_dir):

        print (top, folders, files)
        for file in files:
            filepath = os.path.join(top,file)
            [shutil.copy(__file__, os.path.join(top, i ,import_name)) for i in folders]
            shutil.copy(filepath,filepath+'.d_bak')
            if filepath == __file__ or file == 'xml2obj.py':
                continue
            if file.endswith('.py') == False or os.path.isdir(filepath) or file==import_name:
                continue
            r = open(filepath)
            content = r.read()
            r.close()
            lines = content.split('\n')
            history_index = 0
            last_import_line = ''
            import_added =False
            for line in lines:
                if ( line.strip().startswith('from ') or line.strip().startswith('import ') )and re.match(' *', line).group() == '':
                    last_import_line = line
                if line.strip().startswith('def ') and '(' in line and '):' in line and '__' not in line:

                    indent = re.match(' *', line).group()
                    decorator_line = ''
                    if not import_added:
                        if last_import_line == '':
                            decorator_line += '\n'+indent+'from %s import print_name\n'%import_name.replace('.py', '')
                        else:
                            import_index = content.find(last_import_line)
                            import_indent = re.match(' *', last_import_line).group()
                            import_line = '\n'+import_indent+'from %s import print_name\n'%import_name.replace('.py', '')
                            content = content[:import_index]+import_line+content[import_index:]
                            import_added = True
                    file_index = content[history_index:].find(line)
                    file_index = file_index + history_index
                    decorator_line += indent+'@print_name(print_arg=%s, print_arg_once=%s, print_once=%s)\n' % \
                                             (str(print_arg), str(print_arg_once), str(print_once))
                    content = content[:file_index]+decorator_line+content[file_index:]
                    history_index = file_index

            w=open(filepath,'w')
            w.write(content)
            w.close()


if __name__ == '__main__':
    print os.getcwd()
    print __file__
    if os.path.basename(__file__) != import_name:
        add_decorator(os.getcwd(),print_arg=True, print_arg_once=True, print_once=False)

