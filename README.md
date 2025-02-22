# PAD
Personal advanced directory

# message samples to scan dsc files and copy them into merge folder
```json
{
"client_id":"app_copy_into_merge",
"storage_path":"/source",
"recursive":1,
"file_mask":"*DSC*.*"
}
```

# message sample to scan and store file names in meta

```json
{"client_id":"app_meta_builder", "storage_path":"/source", "recursive":1, "file_mask":"*", "args":"file_name"}
```

```json
{"client_id":"app_meta_builder", "storage_path":"/source", "recursive":1, "file_mask":"*", "args":"parent_folder_path"}
```

# message sample to scan and store all meta for all files
```json
{"client_id":"app_meta_builder", "storage_path":"/source", "recursive":1, "file_mask":"*"}
```
