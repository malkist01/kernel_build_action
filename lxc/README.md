LXC in Android
======
Usage:
```bash
python3 config.py -w <kernel config>
```
in kernel source directory

## About patch
### Patch 1: Solve the problem of panic in the kernel
```bash
python3 patch.py
```

### Patch 2 to solve the problem of running docker using Coccinelle
```bash
python3 patch_cocci.py
```
