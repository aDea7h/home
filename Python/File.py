import os
from pprint import pprint
import tools
import pathlib
# reload(tools)

# TODO Refaire avec pathlib ?


def get_extension_dic():
    extension_dic = {
        '.sc': ('.bgeo.sc', 'cache'),
        '.bgeo': ('.bgeo', 'cache'),
        '.vdb': ('.vdb', 'cache'),
        '.abc': ('.abc', 'cache'),
        '.exr': ('.exr', 'image'),
        '.jpg': ('.exr', 'image'),
        '.hip': ('.hip', 'houdini'),
        '.hipnc': ('.hipnc', 'houdini'),
        '.hiplc': ('.hiplc', 'houdini'),
        '.mp3': ('.mp3', 'audio'),
        '.ogg': ('.ogg', 'audio'),
        '.flac': ('.flac', 'audio'),
        '': ('', 'folder'),
    }
    return extension_dic


class Ls:
    def __init__(self, cmd=None, cmdFormat=None):
        self.defaultCmd = os.listdir
        self.default = True
        if cmd is not None:
            self.cmd = cmd
            self.cmdFormat = cmdFormat
            self.default = False

    def ls(self, path):
        if self.default is True:
            return self.defaultCmd(path)
        else:
            out = self.cmd(self.cmdFormat.format(path))
            if isinstance(out, str) is True:
                out = out.strip().split()
                result = []
                ridx = -1
                merge = False
                for part in out:
                    if part[-1:] == '\\':
                        if merge is True:
                            # print('suffix with merge', result, ridx, part[:-1] + ' ')
                            result[ridx] += part[:-1] + ' '
                        else:
                            # print('suffix no merge', result, ridx, part[:-1] + ' ')
                            result.append(part[:-1] + ' ')
                            ridx += 1
                        merge = True
                    else:
                        if merge is True:
                            # print('no suffix merge', result, ridx, part[:-1] + ' ')
                            result[ridx] += part
                        else:
                            # print('no suffix no merge', result, ridx, part[:-1] + ' ')
                            result.append(part)
                            ridx += 1
                        merge = False
                out = result
            return out

class FileObj:
    def __init__(self, path, name=None, cfg={}, attrs={}):

        self.cfg = {
            'extension_dic': get_extension_dic(),
            'check_existence': True,
            'get_file_info': True,
            'check_validity': False,
        }
        self.cfg.update(cfg)

        if name is None:
            self.path = os.path.dirname(path)
            self.name = os.path.basename(path)
        else:
            self.path = path
            self.name = name

        self.type = None
        self.extension = None

        self.exists = None

        self.size = None
        self.time = None
        self.is_valid = None

        self.__dict__.update(attrs)

        self.get_extension(self.cfg['extension_dic'])
        if self.cfg['check_existence'] is True:
            self.check_existence()
        if self.exists is True and self.cfg['get_file_info'] is True:
            self.get_file_infos()

        if self.cfg['check_validity'] is True:
            self.check_validity()

    def __repr__(self):
        return 'FileObj of {}'.format(self.name)

    def get_extension(self, extension_dic):
        base_name, os_ext = os.path.splitext('{0}/{1}'.format(self.path, self.name))
        if os_ext in extension_dic.keys():
            self.extension = extension_dic[os_ext][0]
            self.type = extension_dic[os_ext][1]
        else:
            self.extension = os_ext
            self.type = "unknown"

    def check_existence(self):
        self.exists = os.path.exists(os.path.join(self.path, self.name))
        if self.exists is False:  # Flag as invalid if folder doesn't exists
            self.is_valid = os.path.exists(self.path)

    def get_file_infos(self):
        self.time = os.path.getmtime(os.path.join(self.path, self.name))
        self.size = os.path.getsize(os.path.join(self.path, self.name))

    def check_validity(self):
        if self.is_valid is False:
            return
        # TODO Test weight
        self.is_valid = True


class SeqFileObj(FileObj):
    """Obj for one single file in a multi files sequence"""
    def __init__(self, path, name=None, cfg={}, attrs={}):
        self.cfg = {
            'idx_separator': ".",
            'idx_pos': -1,
            'get_index': True,
        }
        self.cfg.update(cfg)



        FileObj.__init__(self, path, name, self.cfg, attrs)

        self.idx = None
        self.seq_name = None
        self.__dict__.update(attrs)

        if self.cfg['get_index'] is True:
            self.get_index(self.cfg['idx_separator'], self.cfg['idx_pos'])

    def __repr__(self):
        return 'SeqFileObj of {}'.format(self.name)

    def get_index(self, idx_separator, idx_pos):
        base_name = self.name[:-len(self.extension)]
        if idx_separator in base_name:
            seq_name = base_name.split(idx_separator)
            self.idx = int(seq_name[idx_pos])
            self.seq_name = idx_separator.join(seq_name[:idx_pos])
        else:
            self.idx = False
            self.seq_name = base_name


class Sequence(SeqFileObj):
    # TODO
    """Obj for storing multi SeqFileObj for storing all the seq in multi files seq"""
    def __init__(self, path, name, cfg={}, attrs={}):
        self.cfg = {
        }
        self.cfg.update(cfg)

        self.__dict__.update(attrs)

        SeqFileObj.__init__(self, path, name, self.cfg, attrs)

class BuildTreeFromFileList:
    def __init__(self, fileList, cfg={}, verbose = 0):
        self.fileList = fileList

        self.cfg = {
            'check_existence':False,
        }
        self.cfg.update(cfg)
        self.verbose = verbose

        self.fileTree = self.buildTree(self.fileList)

    def fromListToDictTree(self, list, tree, obj):
        for f in list:
            if f not in tree.keys():
                tree[f] = {self.fromListToDictTree(list.pop(0), {})}
            else:
                tree[f] = {self.fromListToDictTree(list.pop(0), {})}
            if len(list)==0 :
                tree[f]


    def buildTree(self, fileList, tree):
        tree = {}
        for obj in fileList:
            path = pathlib.PurePath(obj.path)
            print(path)
            tree = self.fromListToDictTree(path, tree, obj)


class RecursiveWalk:
    # TODO
    # Add check Sum
    # Add autodetection of file sequence
    # Return as nested dic or fullpath entry dic

    def __init__(self, path, cfg={}, attrs={}, verbose=0):
        self.path = path

        self.cfg = {
            'check_existence': False,
            'get_file_info': True,
            'check_validity': False,
            'file_tree_is_nested': True,
            'limit_recursion': False,
            'max_recursion': 3,
            'filter_files': False,
            'filter_type': [],
            'cmd': None,
            'cmdFormat': None,
        }
        self.cfg.update(cfg)

        self.attrs = {
            'exists': True,
        }
        self.__dict__.update(attrs)
        self.cprint = tools.CustomPrint(0, 0)

        if os.path.exists is False:
            raise Exception('Invalid path')

        #needs cmd, cmdFormat
        self.Ls = Ls(self.cfg['cmd'], self.cfg['cmdFormat'])

        self.file_tree = {}
        if self.cfg['limit_recursion'] is False:
            if self.cfg['file_tree_is_nested'] is True:  # returns flattened dict only ! no nested one
                # raise Exception('Nested dict without max recursion is not implemented yet!')
                self.list_recursive(self.path, self.file_tree, 0)
            for path, dirs, files in os.walk(path):
                for file in files:
                    file_obj = FileObj(path, file, self.cfg, self.attrs)
                    self.file_tree[os.path.join(file_obj.path, file_obj.name)] = file_obj
        else:
            dic = self.list_recursive(self.path, self.file_tree, 0)
            if self.cfg['file_tree_is_nested'] is True:
                self.file_tree = dic
            self.cprint(self.file_tree, 1)

    def list_recursive(self, path, dic, recursion=0):  # return nested dict or flattened dict
        self.cprint('listing files in : {}'.format(path), 1)
        #files = os.listdir(path)
        files = self.Ls.ls(path)
        for file_name in files:
            if os.path.isdir(os.path.join(path, file_name)) is True:
                if recursion + 1 < self.cfg['max_recursion'] or self.cfg['limit_recursion'] is False:
                    result = self.list_recursive(os.path.join(path, file_name), {}, recursion + 1)
                    if result != {} and self.cfg['file_tree_is_nested'] is True:
                        dic[file_name] = result
            else:
                self.cprint((path, file_name), 1)
                file_obj = FileObj(path, file_name, self.cfg, self.attrs)
                if self.filter_file(file_obj) is True:
                    self.cprint('adding file : {}'.format(file_name), 1)
                    if self.cfg['file_tree_is_nested'] is True:
                        dic[file_name] = file_obj
                    else:
                        self.file_tree[os.path.join(file_obj.path, file_obj.name)] = file_obj
                else:
                    self.cprint('rejecting : {}'.format(file_name), 1)
        return dic

    """
    def list_recursive(self, path, dic, recursion=0):
        print('listing files in : {}'.format(path))
        files = os.listdir(path)
        for file_name in files:
            if os.path.isdir(os.path.join(path, file_name)) is True:
                if recursion + 1 < self.cfg['max_recursion']:
                    result = self.list_recursive(os.path.join(path, file_name), dic, recursion + 1)
                    if result != {}:
                        dic[file_name] = result
            else:
                file_obj = FileObj(path, file_name, self.cfg, self.attrs)
                if self.filter_file(file_obj) is True:
                    print('adding file : {}'.format(file_name))
                    dic[file_name] = file_obj
                else:
                    print('rejecting : {}'.format(file_name))
        return dic"""

    def filter_file(self, file_obj):
        if self.cfg['filter_files'] is False:
            return True
        elif self.cfg['filter_type'] is not [] and file_obj.type in self.cfg['filter_type']:
            return True
        else:
            return False

    def return_tree(self):
        return self.file_tree

    def obj_print(self, dic, obj_attrs, log_file=None, indent=0):
        if isinstance(dic, dict) is False:
            return
        idt = '    '*indent
        idt_attr = '  '
        for key in sorted(dic):
            obj = dic[key]
            if isinstance(obj, dict) is True:
                ret = '{}{}'.format(idt, key)
                print(ret)
                if log_file is not None:
                    log_file.write(ret+'\n')
                self.obj_print(obj, obj_attrs, log_file, indent+1)
            else:
                ret = '{}-->> {}'.format(idt, obj)
                print(ret)
                if log_file is not None:
                    log_file.write(ret+'\n')
                for attr in obj_attrs:
                    ret = '{}{}-> {} : {}'.format(idt, idt_attr, attr, eval('obj.'+attr))
                    print(ret)
                    if log_file is not None:
                        log_file.write(ret+'\n')

    def print_tree(self, log_file=None):
        if log_file is not None:
            log_file = open(log_file, 'w')
        self.obj_print(self.file_tree, ['name', 'path', 'size', 'time'], log_file)
        # self.obj_print(self.file_tree, ['name'], log_file)
        if log_file is not None:
            log_file.close()


class BuildFromLog:
    # TODO
    # Return full path or nested dict

    def __init__(self, log_file, re_root=[]):
        if os.path.isfile(log_file) is False:
            raise Exception('Log File doesnt exists')

        self.orig_root = None
        self.new_root = None
        if re_root:
            self.orig_root = re_root[0]
            self.new_root = re_root[1]

        log_file = open(log_file, 'r')
        lines = log_file.readlines()
        self.file_tree = {}
        attrs = {'path': None, 'name': None}
        for line in lines:
            if line.strip().startswith('-->> FileObj of '):
                # # Apply found attrs and create new obj
                # if attrs['path'] is None or attrs['name'] is None:
                #     continue
                # file_obj = FileObj(attrs['path'], attrs['name'], attrs=attrs)
                # # dict_path = self.get_dict_path(attrs['path'])
                # # self.file_tree[dict_path] = file_obj
                # self.file_tree[attrs['path']] = file_obj
                if attrs['path'] is None or attrs['name'] is None:
                    continue
                self.new_file_obj(attrs)

                # erase
                attrs = {'path': None, 'name': None}
                continue

            if line.strip().startswith('-> '):
                attr = line.strip()[3:].split(' : ')
                attrs[attr[0]] = attr[1]

        if attrs['path'] is not None and attrs['name'] is not None:
            self.new_file_obj(attrs)

        log_file.close()

    def new_file_obj(self, attrs):
        if self.orig_root is not None and self.new_root is not None:
            attrs['path'] = attrs['path'].replace(self.orig_root, self.new_root)
        file_obj = FileObj(attrs['path'], attrs['name'], attrs=attrs)
        # dict_path = self.get_dict_path(attrs['path'])
        # self.file_tree[dict_path] = file_obj
        self.file_tree[os.path.join(attrs['path'], attrs['name'])] = file_obj


    def return_tree(self):
        return self.file_tree

    # def get_dict_path(self, path, pointer=''):
    #     dir = os.path.dirname(path)
    #     if path != dir:
    #         base = os.path.basename(path)
    #         self.get_dict_path(dir, '[{}]{}'.format(base, pointer))
    #         return pointer
    #
    #     pointer = '[{}]{}'.format(dir, pointer)
    #     print('-->> dict path '+ pointer)
    #     return pointer


class CompareWithLog:
    def __init__(self, path, log_file):
        self.existing_files = RecursiveWalk(path)
        self.log_files = BuildFromLog(log_file)

        existing = self.existing_files.file_tree
        logged = self.log_files.file_tree
        pprint(logged)
        pprint(existing)

        self.missing = []
        self.new = []
        self.exists = []
        self.same = []
        self.different = []

        self.check_entries(existing, logged)
        self.check_file_stats()

        print(self.same)
        print('----------> different')
        pprint(self.different)
        print('----------> new')
        pprint(self.new)
        print('----------> missing')
        pprint(self.missing)

    def get_dict_items(self, dic, lst=[], msg=''):
        for item in dic:
            if isinstance(dic[item], dict) is True:
                lst = self.get_dict_items(dic[item], lst)
            else:
                lst.append(item)
                print('-- {} file : {}'.format(msg, item))
        return lst

    def check_entries(self, existing, logged):
        for key in dict(existing):
            if key not in logged.keys():
                if isinstance(existing[key], dict) is True:
                    self.get_dict_items(existing[key], self.new, 'new existing')
                else:
                    self.new.append(existing[key])
                    print('-- new existing file : ' +key)
                del existing[key]
            else:
                if isinstance(existing[key], dict) is True:
                    self.check_entries(existing[key], logged[key])
                print('>> existing file : '+key)
                self.exists.append([existing[key], logged[key]])
                del logged[key]

        for key in logged:
            if isinstance(logged[key], dict) is True:
                self.get_dict_items(logged[key], self.missing, 'missing')
            else:
                self.missing.append(logged[key])
                print('missing file '+key)

    def check_file_stats(self):
        for ex_obj, log_obj in self.exists:
            same = True
            attribs = ['time', 'size']
            for attr in attribs:
                if eval('ex_obj.'+attr) != eval('log_obj.'+attr):
                    same = False
                    break;

            if same is True:
                self.same.append(ex_obj)
            else:
                self.different.append(ex_obj)


if __name__ == '__main__':
    # cfg = {
    #     'idx_separator': "_bak",
    # }
    # s = SeqFileObj("F:/Work/Plot Twist/backup/PT_Wall_Push_Test_bak51.hip", cfg=cfg)
    # print('done')
    # print (s)

    path = 'F:\\Work\\Plot Twist'
    path_log = 'F:\\Work\\Plot Twist\\log.txt'
    # r = RecursiveWalk(path)
    # r.print_tree(path_log)


    CompareWithLog(path, path_log)
