from API import SF_APP

if __name__ == '__main__':

    print("欢迎使用SF_Spider V0.2:")

    Downloader = SF_APP.API()
    Downloader.get_cookie_security()

    choice = input("If you want to download single book,please press 1\n"
                   "If you want to download sorted books, please press 2\n"
                   "If you want to download stared books, please press 3:")

    if choice == '1':
        bookid = input("Please input bookid; For instance, the id of '天下第一帝后' is 115157：")
        Downloader.get_chapter(bookid)
        Downloader.download()
    elif choice == '2':
        sort_id = input("Tag '百合': press 74;\nTag ‘系统’: press 109;\nTag ‘逆推’: press 388: ")
        num = input("Please input how many books you want to download: ")
        Downloader.download_sort(int(num), sort_id)
    elif choice == '3':
        Downloader.download_stared()

    else:
        print("Please input correct number")


