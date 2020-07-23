import hou
import os
from time import localtime, strftime
import shutil

"""
 
 
 Old use ProjectManager instead
 
 
 
"""

# TODO
# import delete_old_backups_ in ProjectManager module and delete this one :)
# Use working day sessions while no publish system

if __package__ is None:
    import sys
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if path not in sys.path:
        sys.path.append(path)
import File
import tools
import FileVersionning
reload(FileVersionning)


def delete_old_backups(nbr=10, rem=True):
    """Keeps only a selected nbr of houdini backup files stored in $HIPFILE/backup"""

    cfg = {
        'idx_separator': "_bak",
        'idx_pos': -1,
        'check_existence': False,
        'get_file_info': False,
    }
    full_path = hou.hipFile.path()
    name = hou.hipFile.basename()
    path = full_path[:-len(name)]
    print(path)
    backup_path = os.path.join(path, 'backup')
    if os.path.exists(backup_path) is False:
        raise Exception("No Backup Folder found in : {}".format(backup_path))
    file_list = os.listdir(backup_path)
    file_obj_dict = {}
    for file_name in file_list:
        file_obj = File.SeqFileObj(backup_path, file_name, cfg, {'exists': True})
        if file_obj.seq_name not in file_obj_dict:
            file_obj_dict[file_obj.seq_name] = [file_obj]
        else:
            file_obj_dict[file_obj.seq_name].append(file_obj)
    print('')
    for seq_name in file_obj_dict.keys():
        i = 0
        file_obj_list = file_obj_dict[seq_name]
        file_obj_list.sort(key=lambda x: x.idx, reverse=True)
        while i < nbr:
            keep = file_obj_list.pop(0)
            print('-->> kept : {}'.format(keep.name))
            i += 1

        tools.customPrint(None, 0, 'Removing', True)

        if rem is True:
            for rm_file in file_obj_list:
                print(os.path.join(rm_file.path, rm_file.name))
                os.remove(os.path.join(rm_file.path, rm_file.name))


def publish(publish_folder='_Publish'):
    """Saves hip file and copies it to publish-folder postfixed with time"""
    hou.hipFile.save(None, False)
    full_path = hou.hipFile.path()
    name = hou.hipFile.basename()
    base_name, os_ext = os.path.splitext(name)
    path = full_path[:-len(name)]
    time = localtime()
    local_date = strftime("%Y.%m.%d", time)
    local_time = strftime("%H.%M.%S", time)

    new_name = '{} - {} - {}{}'.format(base_name, local_date, local_time, os_ext)
    publish_path = os.path.join(path, publish_folder, base_name)
    if os.path.exists(publish_path) is False:
        os.makedirs(publish_path)
    publish_path = os.path.join(publish_path, new_name)

    shutil.copy2(full_path, publish_path)
    print('Published to : {}'.format(publish_path))


def versionning():
    hou.hipFile.save(None, False)
    full_path = hou.hipFile.path()
    name = hou.hipFile.basename()
    path = full_path[:-len(name)]

    attrs = {
        'date_versionning': True,
        'version': None,
        'comment': None,
    }

    version = FileVersionning.Version(path, name, attrs)

    attrs

    version.do_publish()
