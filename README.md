# Clumpy

> REST API that you can poll for computer's resource usage for the past hour

## Development

- Install the required dependecies:
  ```
  pip install -r requirements.txt
  ```

## Run

- Run the standalone script:
  ```
  ./clump.py
  ```
  - `--keep-records` (optional) - Keep records for the past number of seconds
  - `--cleanup-interval` (optinal) - Clean up old records every number of seconds
  - `--port` (optinal) - Run on a specific port

## Notes

clump - _a group of things clustered together_

This is the Python version of Clump (https://github.com/matyashlavacek/clump)

_Reimplemented the whole thing in Python since there were some bugs in the go version of psutil (gopsutil) on Windows_
