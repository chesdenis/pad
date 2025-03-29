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

# message to publish batched messages sender
```bash
curl -X POST -u guest:guest \
-H "Content-Type: application/json" \
-d '{
    "properties": {},
    "routing_key": "os_walk_request",
    "payload": "{\"client_id\":\"app_pad_batch_pipe_to_sender\", \"storage_path\":\"/source\", \"recursive\":1, \"file_mask\":\"*\"}",
    "payload_encoding": "string"
}' \
http://localhost:15672/api/exchanges/%2F/amq.default/publish
```


# message to replicate locally
```bash
curl -X POST -u guest:guest \
-H "Content-Type: application/json" \
-d '{
    "properties": {},
    "routing_key": "os_walk_request",
    "payload": "{\"client_id\":\"app_pad_replicate_local\", \"storage_path\":\"/source\", \"recursive\":1, \"file_mask\":\"*\"}",
    "payload_encoding": "string"
}' \
http://localhost:15672/api/exchanges/%2F/amq.default/publish
```


# message sample to collect report storage
```bash
curl -X POST -u guest:guest \
-H "Content-Type: application/json" \
-d '{
    "properties": {},
    "routing_key": "os_walk_request",
    "payload": "{\"client_id\":\"app_report_storage\", \"storage_path\":\"/Volumes/AnnaD/Hive/storage\", \"recursive\":1, \"file_mask\":\"*\"}",
    "payload_encoding": "string"
}' \
http://localhost:15672/api/exchanges/%2F/amq.default/publish
```
```bash
curl -X POST -u guest:guest \
-H "Content-Type: application/json" \
-d '{
    "properties": {},
    "routing_key": "os_walk_request",
    "payload": "{\"client_id\":\"app_report_storage_vs_meta\", \"storage_path\":\"/source\", \"recursive\":1, \"file_mask\":\"*\"}",
    "payload_encoding": "string"
}' \
http://localhost:15672/api/exchanges/%2F/amq.default/publish
```
```bash
curl http://localhost:8080/report
curl http://localhost:8081/report
```
