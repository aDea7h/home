import os

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
        '': ('', 'folder'),
    }
    return extension_dic


class FileObj:
    def __init__(self, path, name=None, cfg={}, attrs={}):

        self.cfg = {
            'extension_dic': get_extension_dic(),
            'check_existence': True,
            'get_file_info': True,
            'check_validity': False,
        }
        self.cfg.update(cfg)

        self.__dict__.update(attrs)

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

        self.get_extension(self.cfg['extension_dic'])
        if self.cfg['check_existence'] is True:
            self.check_existence()
        if self.exists is True and self.cfg['get_file_info'] is True:
            self.get_file_infos()

        if self.cfg['check_validity'] is True:
            self.check_validity()

    def __repr__(self):
        return 'FilObj of {}'.format(self.name)

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
    def __init__(self, path, name=None, cfg={}, attrs={}):
        self.cfg = {
            'idx_separator': ".",
            'idx_pos': -1,
            'get_index': True,
        }
        self.cfg.update(cfg)

        self.__dict__.update(attrs)

        FileObj.__init__(self, path, name, self.cfg, attrs)

        self.idx = None
        self.seq_name = None
        if self.cfg['get_index'] is True:
            self.get_index(self.cfg['idx_separator'], self.cfg['idx_pos'])

    def __repr__(self):
        return 'SeqFilObj of {}'.format(self.name)

    def get_index(self, idx_separator, idx_pos):
        base_name = self.name[:-len(self.extension)]
        if idx_separator in base_name:
            seq_name = base_name.split(idx_separator)
            self.idx = int(seq_name[idx_pos])
            self.seq_name = idx_separator.join(seq_name[:idx_pos])
        else:
            self.idx = False
            self.seq_name = base_name

if __name__ == '__main__':
    cfg = {
        'idx_separator': "_bak",
    }
    s = SeqFileObj("F:/Work/Plot Twist/backup/PT_Wall_Push_Test_bak51.hip", cfg=cfg)
    print('done')
    print (s)