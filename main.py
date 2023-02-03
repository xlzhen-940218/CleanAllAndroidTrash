import os
import subprocess
import time

android_device = ''
list_data = []


def check_media_endswith(path):
    if path.lower().endswith('mp4') or path.lower().endswith('jpg') or path.lower().endswith('webp') or path.lower().endswith(
            'png') or path.lower().endswith('heic') or path.lower().endswith('mov') or path.lower().endswith(
        'avi') or path.lower().endswith('3gp') or path.lower().endswith('mp3') or path.lower().endswith(
        'mid') or path.lower().endswith('wav') or path.lower().endswith('wma') or path.lower().endswith('opus'):
        return True
    else:
        return False


def skip_media():
    media_list = []
    for data in list_data:
        if data['type'].__contains__('image') or data['type'].__contains__('video') or data['type'].__contains__(
                'audio') or check_media_endswith(data['path']):
            media_list.append(data)

    for media in media_list:
        list_data.remove(media)


# delete minimal text
def delete_min_text():
    text_list = []
    for data in list_data:
        if data['type'].__contains__('text') and (
                int(data['size']) < 1024 * 4 or not data['path'].endswith('txt')):  # less than 4k or not txt
            text_list.append(data)
    print(text_list)
    if len(text_list) == 0:
        print('minimal text files is empty, skip')
        return
    delete_text_prompt = input('delete all minimal text files? Please input Y/N?\n')
    if delete_text_prompt.__eq__('Y'):
        all_text_path = ''
        for i in range(len(text_list)):
            list_data.remove(text_list[i])
            all_text_path += ' \'' + text_list[i]['path'] + '\''
            if len(all_text_path) > 8000 or i == len(text_list) - 1:
                result = subprocess.check_output('adb -s {0} shell "rm -rf {1}" '.format(android_device, all_text_path),
                                                 encoding='UTF-8')
                all_text_path = ''
                print('success', i)
    else:
        print('skip delete minimal image files! ')


# delete minimal images
def delete_min_image():
    image_list = []
    for data in list_data:
        if data['type'].__contains__('image') and int(data['size']) < 1024 * 50:
            image_list.append(data)
    print(image_list)
    if len(image_list) == 0:
        print('minimal image files is empty, skip')
        return
    delete_image_prompt = input('delete all minimal image files? Please input Y/N?\n')
    if delete_image_prompt.__eq__('Y'):
        all_image_path = ''
        for i in range(len(image_list)):
            list_data.remove(image_list[i])
            all_image_path += ' \'' + image_list[i]['path'] + '\''
            if len(all_image_path) > 8000 or i == len(image_list) - 1:
                result = subprocess.check_output(
                    'adb -s {0} shell "rm -rf {1}" '.format(android_device, all_image_path),
                    encoding='UTF-8')
                all_image_path = ''
                print('success', i)
    else:
        print('skip delete minimal image files! ')


# delete zip
def delete_zip():
    zip_list = []
    for data in list_data:
        if data['type'].__contains__('archive'):
            zip_list.append(data)
    print(zip_list)
    if len(zip_list) == 0:
        print('compress files is empty, skip')
        return
    delete_zip_prompt = input('delete all compress files? Please input Y/N?\n')
    if delete_zip_prompt.__eq__('Y'):
        all_zip_path = ''
        for i in range(len(zip_list)):
            list_data.remove(zip_list[i])
            all_zip_path += ' \'' + zip_list[i]['path'] + '\''
            if len(all_zip_path) > 8000 or i == len(zip_list) - 1:
                result = subprocess.check_output('adb -s {0} shell "rm -rf {1}" '.format(android_device, all_zip_path),
                                                 encoding='UTF-8')
                all_zip_path = ''
                print('success', i)
    else:
        print('skip delete compress files! ')


def get_type(paths):
    types = []
    all_path = ''
    for i in range(len(paths)):
        all_path += ' \'' + paths[i] + '\''
        if len(all_path) > 8000 or i == len(paths) - 1:
            print('get end suffix by index', i)
            result = subprocess.check_output(
                'adb -s {0} shell "file {1}" '.format(android_device, all_path), encoding='UTF-8')
            results = result.split('\n')

            for r in results:
                if len(r) > 0:
                    types.append(r.split(':')[1].strip())
            all_path = ''
    return types


def scan_trash(data):
    dir_path = '{0}/'.format(data['path'])
    print('ready scan dir path : ', dir_path)
    try:
        result = subprocess.check_output('adb -s {0} shell "ls -a -l \'{1}\'" '.format(android_device, dir_path),
                                         encoding='UTF-8')
        filenames = subprocess.check_output('adb -s {0} shell "ls -a \'{1}\'" '.format(android_device, dir_path),
                                            encoding='UTF-8').split('\n')
        results = result.split('\n')
        results.pop(0)
        temp_list_data = []
        for r in results:
            if filenames[len(temp_list_data)].__contains__(' '):
                r = r.replace(filenames[len(temp_list_data)], 'filename').strip()
            temp = r.split(' ')
            if len(temp) > 1:
                position = 0
                permission = temp[position]
                position += 1
                if temp[position].__eq__(''):
                    position += 1
                filetype = 'file'
                if int(temp[position]) > 1:
                    filetype = 'directory'
                temp_list_data.append({'permission': permission,
                                       'size': temp[len(temp) - 4],
                                       'date': '{0}-{1}'.format(temp[len(temp) - 3], temp[len(temp) - 2]),
                                       'path': '{0}{1}'.format(dir_path, filenames[len(temp_list_data)]),
                                       'type': filetype})

        list_data.extend(temp_list_data)
        for data in temp_list_data:
            if data['type'].__eq__('directory') and not data['path'].endswith('/.') and not data['path'].endswith(
                    '/..'):
                scan_trash(data)
    except:  # This is file, need retry put type
        data['type'] = 'file'


def wait_connect():
    result = os.popen('adb devices').read()
    while not result.__contains__("\tdevice"):
        result = os.popen('adb devices')
        print(result)
    results = result.split('\n')
    global android_device
    android_device = results[1].split('\t')[0]


# Press the green button in the gutter to run the script.
def check_document_endswith(path):
    if path.lower().endswith('docx') or path.lower().endswith('pptx') or path.lower().endswith(
            'ppt') or path.lower().endswith('doc') or path.lower().endswith('txt') or path.lower().endswith(
        'dot') or path.lower().endswith('xls') or path.lower().endswith('xlsx') or path.lower().endswith(
        'epub') or path.lower().endswith('chm') or path.lower().endswith('pdf'):
        return True
    else:
        return False


def skip_document():
    document_list = []
    for data in list_data:
        if data['type'].__contains__('document') or data['type'].__contains__('text') or check_document_endswith(
                data['path']):
            document_list.append(data)

    for document in document_list:
        list_data.remove(document)


# The empty folder was deleted once when the file was just deleted, and then again
def delete_empty_folder():
    for data in list_data:
        if data['type'].__eq__('directory') and not data['path'].startswith(
                '/sdcard/Android'):  # if directory is Android need skip
            try:
                result = subprocess.check_output(
                    'adb -s {0} shell "ls -a -l \'{1}\'" '.format(android_device, data['path']),
                    encoding='UTF-8')
                while result.__contains__('total 0'):
                    result = subprocess.check_output(
                        'adb -s {0} shell "rm -rf \'{1}\'" '.format(android_device, data['path']),
                        encoding='UTF-8')
                    print('success', data['path'])
                    data['path'] = os.path.split(data['path'])[0]  # Recursive deletion
                    result = subprocess.check_output(
                        'adb -s {0} shell "ls -a -l \'{1}\'" '.format(android_device, data['path']),
                        encoding='UTF-8')
            except:
                print('folder already delete...')


def delete_other_files():
    for data in list_data:
        if not data['type'].__eq__('directory'):
            result = subprocess.check_output('adb -s {0} shell "rm -rf \'{1}\'" '.format(android_device, data['path']),
                                             encoding='UTF-8')
            print('success', data['path'])
        else:
            if not data['path'].startswith('/sdcard/Android'):  # if directory is Android need skip
                result = subprocess.check_output(
                    'adb -s {0} shell "ls -a -l \'{1}\'" '.format(android_device, data['path']),
                    encoding='UTF-8')
                if result.__contains__('total 0'):
                    result = subprocess.check_output(
                        'adb -s {0} shell "rm -rf \'{1}\'" '.format(android_device, data['path']),
                        encoding='UTF-8')
                    print('success', data['path'])


if __name__ == '__main__':
    print('Welcome use clean all android trash!')
    print('Please connect android device! and open usb debug.')
    wait_connect()
    scan_trash({'path': '/sdcard'})
    paths = []
    for file in list_data:
        if not file['type'].__eq__('directory'):
            paths.append(file['path'])

    types = get_type(paths)
    index = 0
    for i in range(len(list_data)):
        if not list_data[i]['type'].__eq__('directory'):
            list_data[i]['type'] = types[index]
            index += 1
    delete_zip()
    delete_min_image()
    delete_min_text()
    skip_media()
    skip_document()
    delete_other_files()
    delete_empty_folder()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
