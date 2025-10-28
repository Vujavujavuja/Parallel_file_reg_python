# Parallel File System

## Project Overview

This is a simple proof-of-concept for a **parallel file system** interface. Basically, it takes a file, breaks it into pieces, stores those pieces across the system using multiple processes, and then can put it back together later. It's built for **basic concurrency** and not losing data (mostly). We built the simple stuff: `put`, `get`, and `delete`.

If you need to move big files fast, this is where you start.

***

## ⚙️ How It Works (The Bare Minimum)

We use Python's built-in tools to handle the heavy lifting. The core principle is "divide and conquer."

### Key Mechanisms

* **File Partitioning:** When you run `put`, the file gets split into fixed-size chunks (parts).
* **Parallel Processing:** We use a **multiprocessing pool** (equal to your CPU count) to handle the parts concurrently. Each part is processed and stored independently.
* **Concurrency Control:** We use a **threading condition** (`memory_usage_lock`) to enforce a **Max Memory Limit** and prevent the system from exploding while loading parts into memory. Threads wait their turn if memory is tight.
* **Data Integrity:** Each file part gets a **unique ID**, and we track its **MD5 hash** during storage. If the hash doesn't match on retrieval, we know something went wrong, and we skip the bad part.

### Registry

We use two simple registry classes (`FileRegistry` and `PartRegistry`) to track everything, since we can't just trust the file paths alone:

1.  **File Registry:** Tracks the file name, its status, and the list of part IDs that belong to it.
2.  **Part Registry:** Tracks the location, status, and MD5 hash for every individual file part.

***

## 🚀 Usage

You interact with the system via a basic command-line loop.

### Commands

| Command | Action | Notes |
| :--- | :--- | :--- |
| **`put <file_path>`** | Stores a file in the system. Runs in a new thread. | Breaks file into parts, processes them in parallel. |
| **`get <file_id>`** | Retrieves a file by its ID. Runs in a new thread. | Reconstructs the file from its parts in parallel. |
| **`delete <file_id>`** | Removes a file and all its parts. Runs in a new thread. | Deletes all associated parts in parallel. |
| **`list`** | Shows all files currently tracked by the system. | Prints ID, name, and current status. |
| **`exit`** | Shuts down the system and waits for all active operations to finish. | Don't forget to wait. |

### Example

```bash
put /path/to/my/big/data.file
list
get 1
```
## 📦 Setup & Dependencies
It's all Python. Just make sure the stuff in the import list is installed, especially process, storage.*, and loader, which are assumed to be separate files you have lying around.

os, threading, multiprocessing (Standard Python)

zlib, hashlib, uuid (Standard Python)

External: process.py, storage/fileregistry.py, storage/partregistry.py, loader.py

This project is not production-ready; it's just a sandbox to understand the parallel processing concepts. Don't use it for anything important.
