from collections import namedtuple

NameLink = namedtuple("NameLink", 'name url')
default_email_folder = 'EMAIL_FOLDER_WITH_PRICES_NAME'
default_remote_folder = 'YADISK_FOLDER_WHERE_TO_STORE_FILES'

suppliers = (
    NameLink(name='smth.xlsx', url='https://www.urllink.com/smth'),
)
