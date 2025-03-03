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
{
"client_id":"app_meta_builder",
"storage_path":"/source",
"recursive":1,
"file_mask":"*",
"args":
    {
        "meta_name":"file_name",
        "rewrite":true
    }
}
```

# message sample to scan and store file hash in meta

```json
{
"client_id":"app_meta_builder",
"storage_path":"/source",
"recursive":1,
"file_mask":"*",
"args":
    {
        "meta_name":"md5_hash",
        "rewrite":true
    }
}
```

# message sample to scan and store all meta for all files
```json
{"client_id":"app_meta_builder", "storage_path":"/source", "recursive":1, "file_mask":"*"}
```

# message sample to rescan and regenerate image averages based on preview
```json
{"client_id":"app_meta_builder", "storage_path":"/source", "recursive":1, "file_mask":"*"}
```

# message sample to rescan and regenerate face hashes based on preview
```json
{"client_id":"app_face_hash_builder", "storage_path":"/source", "recursive":1, "file_mask":"*DSC_1456.NEF"}
```
