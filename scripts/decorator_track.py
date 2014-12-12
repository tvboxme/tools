#!/usr/bin/env python
# encoding: utf-8

import pickle
from functools import wraps
import sys,types
import shutil
n = 0
indent = 0
import_name = 'decorate_.py'
postfix_bak = '.d_bak'
list = []
def print_name(print_arg=True, print_arg_once=True, print_once=False):
    """ general decorator
    print arg: print arg and result
    print arg once: print arg and result once
    print once:  do not print duplicate arg and result
    """
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            global n, last_func,indent
            indent+=1
            simple_item = func.__module__+'.'+func.__name__
            print_result = False
            print_result_once = False
            if print_arg:
                print_result = True
                new_item= func.__module__+'.'+func.__name__+':'+str([str(i)[:100] for i in args])+' '+str(kwargs)[:100]
                if print_arg_once:
                    if simple_item in list:
                        new_item = simple_item
                    else:
                        print_result_once = True
                        list.append(simple_item)
            else:
                new_item = simple_item
            if print_once and new_item in list:
                print_result = False
            else:
                print '*'*indent,'Calling',new_item
                list.append(new_item)
            #this will print only if there is exception
            #f = sys.exc_info()[2].tb_frame.f_back
            #print f.f_code
            result = func(*args, **kwargs)
            if print_result_once:
                print '*'*indent,'Ret of  %s: ' % (func.__module__+'.'+func.__name__), result
            elif print_result:
                print '*'*indent,'Ret of  %s: ' % (func.__module__+'.'+func.__name__), result
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
        if os.path.isfile(os.path.join(top, import_name)):
            os.remove(os.path.join(top, import_name))
        print (top, folders, files)
        for file in files:
            filepath = os.path.join(top,file)
            if file.endswith(postfix_bak):
                shutil.move(filepath,filepath[:-1*len(postfix_bak)])

def add_decorator(source_dir=None, print_arg=True, print_arg_once=True, print_once=False, max_levl=0,excludes=None):
    # source_dir='/home/jessiex/git/stress/scripts'
    if source_dir == None:
        source_dir = os.getcwd()
    shutil.copy(__file__, os.path.join(source_dir, import_name))
    assert type(excludes) == type([])
    for (top, folders, files) in os.walk(source_dir):
        if max_levl>0 and top.replace(source_dir,'').split('/') < max_levl+1:
            return
        for file in files:
            if file in excludes:
                continue
            filepath = os.path.join(top,file)
            if filepath == __file__ or file == 'xml2obj.py':
                continue
            if file.endswith('.py') == False or os.path.isdir(filepath) or file.endswith(postfix_bak):
                continue
            if not filepath.endswith(postfix_bak) and filepath.endswith('.py') and file!=import_name:
                shutil.copy(filepath,filepath+postfix_bak)
            if  top != source_dir:
                shutil.copy(os.path.join(source_dir, import_name), os.path.join(top, import_name))
            elif file == import_name:
                continue
            print filepath
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

                if (line.strip().startswith('def ') or (line.strip().startswith('class ')))and ':' in line and '__' not in line :
                    indent = re.match(' *', line).group()
                    decorator_line = ''
                    if not import_added:
                        if last_import_line == '':
                            decorator_line += '\n'+indent+'from %s import print_name\n'%import_name.replace('.py', '')
                            if indent == '':
                                import_added = True
                        else:
                            import_index = content.find(last_import_line)
                            import_indent = re.match(' *', last_import_line).group()
                            import_line = '\n'+import_indent+'from %s import print_name\n'%import_name.replace('.py', '')
                            content = content[:import_index]+import_line+content[import_index:]
                            import_added = True
                    file_index = content[history_index:].find(line)
                    file_index = file_index + history_index
                    if line.strip().startswith('def '):
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
        add_decorator(os.getcwd(),print_arg=True, print_arg_once=True, print_once=False, max_levl=0, excludes=['message.py','loggerhelper.py','errors.py'])

