# uploader
Easily automate subject creatin and data uploads to the Mint Labs platform.

# Basic how to

```bash
python3 upload.py --user "mintuser" --password "mintpassword" --project "project" --info "file.csv" --dir "data/"
```

You must have a csv file with the following structure:

```
File     ,    Subject,  Gender, Metadata1, Metadata2,...
         ,           ,        ,     type1,     type2,...
filepath1, subj_name1, gender1,   meta1_1,   meta2_1,...
filepath2, subj_name2, gender2,   meta1_2,   meta2_2,...
```

Two columns are mandatory: File and Subject.
-   File will contain the name of the file containing the subject data. This is either an absolute path
    or a path relative to "dir", which is passed to the script as an argument (--dir).
-   Subject contains the name of the subject, as it will appear in the project

The rest of the columns are a variable number metadata parameters.

The second row is used to define the type of the metadata parameters. These can be:
-   "integer"
-   "date"
-   "string"
-   "list"
-   "decimal"

The actual data is contained from rows 3 to the end of the file.

# Threaded upload
By default the upload is done using 5 threads (ie. 5 files are uploaded at the same time). This can be modified
with the argument -n or --threads, indicating the number of threads (ie the number of simultaneous uploads).
Eg.
```bash
python3 upload.py --user "mintuser" --password "mintpassword" --project "project" --info "file.csv" --dir "data/" --threads 10
```

will upload 10 files at the same time
