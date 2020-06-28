from tkinter import *
from tkinter import filedialog
from shutil import copyfile as CP
import botocore.exceptions as exc

import boto3
from Credential.User_credential import get_keys

root = Tk()
root.title("S3-Browser    By Hooman Hesamyan V2.0")

# root.geometry('800x600')
user_access_key_id = ''
user_secret_access_key = ''
user_endpoint_url = ''
s3 = ''
s3_client = ''


def init_services(aws_access_key_id, aws_secret_access_key):
    global s3
    global s3_client
    s3_client = boto3.client('s3',
                             # endpoint_url=user_access_key_id,
                             aws_access_key_id=user_access_key_id,
                             aws_secret_access_key=user_secret_access_key
                             )
    s3 = boto3.resource('s3',
                        # endpoint_url=user_access_key_id,
                        aws_access_key_id=user_access_key_id,
                        aws_secret_access_key=user_secret_access_key
                        )


def open_input():
    global user_access_key_id
    global user_secret_access_key
    global s3
    global s3_client

    user_access_key_id = aws_key_id_entry.get()
    user_secret_access_key = aws_secret_access_key_entry.get()

    iterate_over_buckets(user_access_key_id, user_secret_access_key)

    aws_key_id_entry.delete(0, END)
    aws_secret_access_key_entry.delete(0, END)


def open_csv():
    global user_access_key_id
    global user_secret_access_key
    global s3
    global s3_client
    global aws_login_with_csv
    root.filename = filedialog.askopenfilename(initialdir="~/Downloads",
                                               title="Select key.csv file",
                                               filetypes=(("csv files", "*.csv"), ("txt files", "*.txt")))

    aws_get_key_label2 = Label(aws_login_with_csv, text="Logged in using: " + root.filename.split('/')[-1])
    aws_get_key_label2.grid(row=2, column=2, columnspan=3)
    user_access_key_id, user_secret_access_key = get_keys(root.filename)
    aws_browser_button.pack()


def iterate_over_buckets(aws_access_key_id, aws_secret_access_key):
    global s3
    global s3_client
    init_services(aws_access_key_id, aws_secret_access_key)
    buckets = Tk()
    buckets.title("Buckets")
    bucket_label = LabelFrame(buckets, text="All buckets are:")
    list_box = Listbox(bucket_label, bg="#e8ae95", selectmode=SINGLE, width=50, selectbackground="#bf06b9", cursor="")
    list_box.activate(END)
    action_box = LabelFrame(buckets, text="Choose action:")

    i = 1
    for bucket in s3.buckets.all():
        list_box.insert(i, bucket.name)
        i += 1

    # list_box.yview()
    list_box.pack()
    bucket_label.pack()

    download_button = Button(action_box, text="Open!", padx=50,
                             command=lambda: iterate_over_files(
                                 list_box.get(0) if len(list_box.curselection()) == 0 else list_box.get(
                                     list_box.curselection())))
    upload_button = Button(action_box, text="Upload!", padx=50,
                           command=lambda: upload_file(
                               list_box.get(0) if len(list_box.curselection()) == 0 else list_box.get(
                                   list_box.curselection())))
    download_button.grid(row=0, column=0)
    upload_button.grid(row=0, column=1)
    action_box.pack()


def iterate_over_files(aws_bucket_name):
    global s3
    if len(aws_bucket_name) == 0:
        return
    files = Tk()
    files.title("Files")
    files_label = LabelFrame(files, text="All files are:")
    Label(files_label, text="Inside bucket: " + aws_bucket_name, fg="#b82c06").pack()
    succeed_response = Label(files_label, text="Download succeed", fg="#b82c06")
    failed_response = Label(files_label, text="Download failed", fg="#b82c06")
    list_box = Listbox(files_label, bg="#abe895", selectmode=SINGLE, width=50, selectbackground="#19bf06")

    for file in s3.Bucket(aws_bucket_name).objects.all():
        i = 1
        list_box.insert(i, file.key)
        i += 1
    list_box.pack()
    files_label.pack()
    select_button = Button(files_label, text="Download file!", padx=50,
                           command=lambda: download_file(aws_bucket_name, list_box.get(list_box.curselection()), succeed_response, failed_response))
    select_button.pack()


def download_file(aws_bucket_name, aws_object_name, okay, fail):
    global s3_client
    file_name = '.' + str(aws_object_name)[:].split('/')[-1]
    try:
        s3_client.download_file(aws_bucket_name, aws_object_name, file_name)
        okay.pack()
        # CP(file_name, '~/Desktop')
        print("Download was successful")

    except exc.ClientError:
        fail.pack()
        print("")


def upload_file(aws_bucket_name):
    global s3
    global s3_client
    print(aws_bucket_name)

    files = Tk()
    files.title("Files")
    files_label = LabelFrame(files, text="Upload a file:")
    upload_key_label = LabelFrame(files)
    Label(files_label, text="Selected bucket: " + aws_bucket_name, fg="#b82c06").pack()
    Label(upload_key_label, text="Choose a name for uploading file: ").grid(row=0, column=0)
    selected_name_file = Entry(upload_key_label)
    succeed_response = Label(files_label, text="Uploading succeed!")
    failed_response = Label(files_label, text="Uploading failed!")
    selected_name_file.grid(row=0, column=1)
    Button(upload_key_label, text="Upload selected file",
           command=lambda: upload(root.filename, aws_bucket_name, selected_name_file.get())).grid(row=2, column=0, columnspan=2)

    files_label.pack()
    upload_key_label.pack()

    root.filename = filedialog.askopenfilename(initialdir="~/Pictures",
                                               title="Select a file to upload",
                                               filetypes=(("all files", "*.*"),
                                                          ("image files",
                                                           ("*.jpg", "*.jpeg", "*.png")),
                                                          ("document files",
                                                           ("*.doc", "*.docs", "*.odt", "*.pdf", "*.txt"))))

    Label(files_label, text="Selected file: " + root.filename.split('/')[-1], fg="#b82c06").pack()

    def upload(local_file, bucket_name, s3_file):

        try:
            s3_client.upload_file(local_file, bucket_name, s3_file if len(s3_file) != 0 else "anonymous.gen")
            succeed_response.pack()
            print("Upload Succeed")

        except FileNotFoundError:
            failed_response.pack()
            print("failed to upload...")


introduction = Label(root, text="For using AWS please insert these information:", fg="#69054b", font=("Arial", 16),
                     justify=LEFT,
                     padx=200, relief=SUNKEN, bd=1)
aws_login_with_keys = LabelFrame(root, text="Login with keys")
aws_login_with_csv = LabelFrame(root, text="Login with CSV file")
aws_browse_content = LabelFrame(root, text="Browser...")

aws_key_id_label = Label(aws_login_with_keys, text="AWS Access Key Id: ", fg="#052b69", anchor=E, relief=SUNKEN, bd=1,
                         padx=50)
aws_secret_access_key_label = Label(aws_login_with_keys, text="AWS Secret Key: ", fg="#052b69", anchor=E, relief=SUNKEN,
                                    bd=1, padx=50)
aws_get_key_label = Label(aws_login_with_csv, text="Try to log in!")

aws_key_id_entry = Entry(aws_login_with_keys)
aws_secret_access_key_entry = Entry(aws_login_with_keys)

aws_submit_keys = Button(aws_login_with_keys, text="Login!", padx=50, command=lambda: open_input(), fg="#052b69",
                         borderwidth="2", state=NORMAL)
aws_get_key_file = Button(aws_login_with_csv, text="Login with credential file...", command=lambda: open_csv(),
                          fg="#052b69",
                          borderwidth="2", padx=50)
aws_browser_button = Button(aws_browse_content, text="Browse all buckets...", command=lambda: iterate_over_buckets(user_access_key_id, user_secret_access_key), padx=100)

introduction.grid(row=0, column=0, columnspan=6)
aws_login_with_keys.grid(row=1, column=1)
aws_login_with_csv.grid(row=1, column=2)
aws_browse_content.grid(row=2, column=1, columnspan=2)


aws_key_id_label.grid(row=1, column=0, sticky=W + E)
aws_secret_access_key_label.grid(row=2, column=0, sticky=W + E)
aws_key_id_entry.grid(row=1, column=1)
aws_secret_access_key_entry.grid(row=2, column=1)
aws_submit_keys.grid(row=3, column=0, columnspan=2)
aws_get_key_file.grid(row=1, column=2, columnspan=3)
aws_get_key_label.grid(row=2, column=2, columnspan=3)
# aws_browser_button.pack()

root.mainloop()
