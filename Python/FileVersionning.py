from time import localtime, strftime
import os
import shutil
import json
from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWUSR
import tools
#reload(tools)

# TODO
# if cache publish sends to HDD
# if other publish kept to SSD
# overwrites publish and comments for caches file with same versionning (with warning)
# new publish for regular files even with same versionning
# auto compute versionup if date_versionning is False ?
# unlock readonly file on re import file

class Version:
    def __init__(self, path, name, attrs={}):
        self.path = path
        self.name = name
        self.publish_path = None

        self.publish_folder = '_Publish'
        self.comments_file = '{} comments.json'.format(self.name)
        self.date_versionning = True
        self.version = None
        self.comment = None
        self.todo = None
        self.done = None
        self.flags = None
        self.date = None
        self.display_date = None

        self.exported_attrs = ['display_date', 'version', 'comment', 'todo', 'done', 'flags', 'name', 'path', 'publish_path']

        self.__dict__.update(attrs)

        self.cprint = tools.CustomPrint(0, 0)

        if self.date is None:
            self.date = localtime()

        if self.display_date is None:
            local_date = strftime("%Y.%m.%d", self.date)
            local_time = strftime("%H.%M.%S", self.date)
            self.display_date = '{}-{}'.format(local_date, local_time)

        if self.publish_path is None:
            if self.date_versionning is True:
                self.publish_path = os.path.join(path, self.publish_folder,
                                                 '{} - {}'.format(self.display_date, self.name))
            else:
                if self.version is None:
                    raise Exception("no version given")
                self.publish_path = os.path.join(path, self.publish_folder,
                                                 '{} - {}'.format(self.version, self.name))

    def do_publish(self):
        if os.path.exists(self.publish_path) is False:
            os.makedirs(self.publish_path)
        if self.date_versionning is True:
            self.date_publish_comment()
        else:
            self.version_publish_comment()
        publish_path = os.path.join(self.publish_path, self.name)
        shutil.copy2(os.path.join(self.path, self.name), publish_path)
        self.set_read_only_status(publish_path, True)
        print('Published to : {}'.format(publish_path))

    def set_read_only_status(self, file_path, read_only=False):
        if read_only is True:
            os.chmod(file_path, S_IREAD | S_IRGRP | S_IROTH)
        else:
            os.chmod(file_path, S_IWUSR | S_IREAD)

    def comment_content(self):
        content = {}
        for val in self.exported_attrs:
            content[val] = eval('self.'+val)
        return content

    def date_publish_comment(self):
        json_path = os.path.join(self.path, self.publish_folder)
        if os.path.isdir(json_path) is False:
            os.makedirs(json_path)
        json_path = os.path.join(json_path, self.comments_file)
        self.cprint(json_path, 1)
        # content = ''
        comments = {}
        if os.path.exists(json_path) is True:
            # with open(json_path, 'r') as json_file:
            #     # json_file = open(json_path, 'w+')
            #     content = json_file.read()

            with open(json_path) as json_file:
                comments = json.load(json_file)
        # if content not in ['', {}]:
        #     print(content)
        #     comments = json.loads(content)
        #     print(comments)
        # else:
        #     comments = {}
        self.cprint(comments, 1, 'Comments')
        comments[self.display_date] = self.comment_content()
        self.cprint(comments, 1)
        with open(json_path, 'w') as json_file:
            json.dump(comments, json_file)
            # json_file.close()

    def version_publish_comment(self):
        pass

    def return_version(self, content, version='latest'):
        if version == 'latest':
            return content[sorted(content.keys())[-1]]
        elif version in content.keys():
            return content[version]
        else:
            raise Exception('version {} not found in json file'.format(version))

    def get_version_from_log(self, json_path=None, version='latest'):
        if json_path is None:
            json_path = os.path.join(self.path, self.publish_folder, self.comments_file)
        if os.path.exists(json_path) is False:
            print('Invalid file : '+json_path)
            return

        with open(json_path) as json_file:
            content = json.load(json_file)

        attr_dic = self.return_version(content, version)
        if 'flags' in attr_dic:
            del(attr_dic['flags'])
        self.__dict__.update(attr_dic)

