KernelSU scripts
=====
## Overview
This repository contains scripts designed to assist in patching non-GKI (Generic Kernel Image) kernels for KernelSU integration. These scripts automate the process of modifying kernel source code, ensuring compatibility with KernelSU while maintaining reliability and cleanliness.

The following scripts are included:
1. **`apply_cocci.py`**: A Python script that leverages **Coccinelle**, a program matching and transformation tool, to apply patches in a cleaner and more reliable manner.

---

## Dependencies

### For `apply_cocci.py`
- **Coccinelle**: A powerful tool for pattern matching and transformation in C code. It ensures precise and reliable patching.
- **GNU Parallel**: Used to parallelize tasks, such as downloading multiple `.cocci` patches simultaneously.
- **curl**: A command-line tool for transferring data with URLs, used here for downloading `.cocci` patch files.

Before running the scripts, ensure all dependencies are installed on your system. You can install them using your package manager:
```bash
# For Debian/Ubuntu-based systems
sudo apt update
sudo apt install coccinelle aria2 python3

# For Fedora/RHEL-based systems
sudo dnf install coccinelle aria2 python3
```

---

## Usage Instructions

### General Setup
1. Clone the repository containing the scripts and navigate to the directory:
   ```bash
   git clone https://github.com/dabao1955/kernel_build_action.git
   cd kernel_build_action/kernelsu
   ```

2. Ensure you have the kernel source code available. Navigate to the root directory of the kernel source where you intend to apply the patches.

3. Run the script:

### Running `apply_cocci.py`
The `apply_cocci.py` script is the recommended method for patching due to its reliability and clean output. It downloads `.cocci` patch files and applies them using Coccinelle.

To execute:
```bash
python3 apply_cocci.py
```

#### How It Works:
1. The script fetches the required `.cocci` patch files from a remote repository using `aria2c`.
2. It applies the patches to the kernel source code using Coccinelle.
3. The script processes files sequentially with proper error handling.

---

## Advantages of Each Script

### `apply_cocci.py`
- **Precision**: Coccinelle ensures accurate matching and transformation of C code.
- **Reliability**: Reduces the risk of introducing errors during patching.
- **Scalability**: Handles complex patches more effectively than `sed`.

---

## Notes and Best Practices
1. **Backup Your Kernel Source**: Always create a backup of your kernel source directory before applying patches.
2. **Test Thoroughly**: After patching, compile the kernel and test it in a controlled environment to ensure stability.
3. **Customization**: If you need to modify the scripts or add new patches, refer to the documentation for `sed` and Coccinelle to understand their syntax and capabilities.
4. **Environment Compatibility**: Ensure your development environment meets the requirements for building the kernel and running the scripts.

---

## Troubleshooting
- **Missing Dependencies**: If you encounter errors related to missing tools, verify that all dependencies are installed and accessible in your PATH.
- **Patch Conflicts**: In case of conflicts during patching, review the affected files manually and resolve discrepancies.
- **Script Errors**: Check the script logs for detailed error messages. Modify the scripts or patches as needed to address specific issues.

---

## Conclusion
These scripts provide a robust solution for integrating KernelSU into non-GKI kernels. By leveraging Coccinelle with Python, they ensure reliable patching for complex transformations. Follow the instructions carefully, and enjoy a streamlined patching process for your kernel development workflow.

For further assistance or contributions, feel free to open an issue or submit a pull request in the repository.
