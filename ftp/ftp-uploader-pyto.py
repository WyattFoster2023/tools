from ftp import FTPUploader

uploader = FTPUploader()

attached = pasteboard.shortcuts_attachments()
files = []

for item in attached:
    if item.get_file_path() == None:
        try:
            with open(item.get_file_name(), "rb") as f:
                f.write(item.data())
            files.append(item.get_file_name())
            print(f'Cached {item.get_file_name()}')
        except Exception as e:
            print(f'Error caching {item.get_file_name()}')
            print(e)
        
    else:
        print(f'Saved ')
        files.append(item.get_file_path())

for file in files:
    u

