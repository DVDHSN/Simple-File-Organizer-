# File Organizer

A modern file organizer application with a dark theme, built with Python and DearPyGui.

## Features

- Browse and navigate through files and directories
- Sort files by name, date modified, and size
- Organize files into categories (Images, Documents, etc.)
- Dark theme for comfortable usage
- Cross-platform (Windows, macOS, Linux)
- Single executable build available
- Navigate up directory tree
- View file details (name, size, modification date)

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Method 1: From Source

1. Clone or download this repository
2. Open a terminal/command prompt in the project directory
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
4. Run the application:
   ```
   python file_organizer.py
   ```

### Method 2: Download Executable (Windows)

1. Download the latest release from the [Releases]([https://github.com/yourusername/FileOrganizer/releases](https://github.com/DVDHSN/Simple-File-Organizer-)) page
2. Run the `FileOrganizer.exe` file

## Building from Source

To build the executable yourself:

1. Make sure you have Python and pip installed
2. Install the build requirements:
   ```
   pip install pyinstaller
   ```
3. Run the build script:
   ```
   python build.py
   ```
4. The executable will be in the `dist` folder

### Controls
- Use the "Up" button to navigate to the parent directory
- Click "Select Directory" to choose a different directory
- Use the dropdown menu to select a sorting method

## Requirements

- Python 3.7+
- dearpygui>=1.10.0

### Screenshots
![Screenshot 2025-06-09 200322](https://github.com/user-attachments/assets/dd40f1bd-3994-4258-a9dd-3c52bacd0ee7)
Simple yet effective UI. Clean, Sleek, Modern and Easy to use

![Screenshot 2025-06-09 200421](https://github.com/user-attachments/assets/1ed39ab2-02dc-4cea-859b-f66084c66b38)
Sorts files based on its type 

![Screenshot 2025-06-09 200455](https://github.com/user-attachments/assets/23fcc118-deca-467d-a0f6-fc22363bee72)
Also sorts files alphabetically (A-Z)/(Z-A), Last Modified(Latest or Oldest) and even file size(Large to Small or Small to Large)




