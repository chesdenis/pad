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
{"client_id":"app_image_hash_builder", "storage_path":"/source", "recursive":1, "file_mask":"*"}
```

# message sample to rescan and regenerate face hashes based on preview
```json
{"client_id":"app_face_hash_builder", "storage_path":"/source", "recursive":1, "file_mask":"*"}
```


# message sample to collect report storage
```json
{"client_id":"app_report_storage", "storage_path":"/source", "recursive":1, "file_mask":"*"}
```
```json
{"client_id":"app_report_storage_vs_meta", "storage_path":"/source", "recursive":1, "file_mask":"*"}
```
```bash
curl http://localhost:8080/report
curl http://localhost:8080/clear
```
```bash
curl http://localhost:8081/report
curl http://localhost:8081/clear
```
