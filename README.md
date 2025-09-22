# 🌙 Nighttime To-Do List

A beautiful, nighttime-themed to-do list application built with PyQt6 for macOS.

## ✨ Features

- **Beautiful UI**: Nighttime mountain theme with purple gradients and starry elements
- **Task Management**: Add, complete, and delete tasks with checkboxes
- **Persistent Storage**: Tasks are automatically saved to `pixel_todo_tasks.json`
- **Interactive Elements**:
  - ✨ Clear completed tasks button
  - 🌙 Close button
  - Double-click to delete tasks
  - Keyboard shortcuts (Escape to close, Delete to remove selected task)
- **Task Counter**: Shows total, pending, and completed task counts
- **Draggable Window**: You can drag the window around your screen
- **Background Image Support**: The app looks for background images in the directory
- **Always on Top**: Stays visible above other windows

## 🚀 Installation

### Option 1: Install from Source (Recommended)

1. **Clone or download this repository**
2. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Build the app:**
   ```bash
   python3 setup.py py2app
   ```

4. **Install to Applications folder:**
   ```bash
   ./install.sh
   ```

### Option 2: Use Pre-built App

1. **Download the app** from the `dist/` folder
2. **Drag `Nighttime To-Do.app`** to your Applications folder
3. **Double-click to run**

## 🎯 How to Use

1. **Add Tasks**: Type in the input field and press Enter or click "⭐ ADD TASK ⭐"
2. **Complete Tasks**: Check off tasks using the checkboxes
3. **Delete Tasks**: Double-click any task to delete it
4. **Clear Completed**: Click the ✨ button to clear all completed tasks
5. **Move Window**: Drag the window around your screen
6. **Keyboard Shortcuts**:
   - `Escape`: Close the app
   - `Delete`: Delete selected task

## 🎨 Customization

### Background Image
Place any of these image files in the app directory for a custom background:
- `background.png`
- `background.jpg`
- `background.jpeg`
- `bg.png`, `bg.jpg`, `bg.jpeg`
- `todo_bg.png`, `todo_bg.jpg`, `todo_bg.jpeg`

### Data Storage
- Tasks are saved in `pixel_todo_tasks.json`
- The file is created automatically in the same directory as the app
- You can backup/restore your tasks by copying this file

## 🛠️ Development

### Requirements
- Python 3.8+
- PyQt6
- py2app (for building standalone app)

### Building from Source
```bash
# Install dependencies
pip3 install -r requirements.txt

# Build the app
python3 setup.py py2app

# The app will be created in dist/Nighttime To-Do.app
```

### Running in Development
```bash
python3 todolist.py
```

## 📱 App Information

- **Name**: Nighttime To-Do List
- **Version**: 3.0.0
- **Bundle ID**: com.mountainapps.nighttime-todo
- **Platform**: macOS (Intel & Apple Silicon)
- **Framework**: PyQt6

## 🐛 Troubleshooting

### App Won't Open
1. Make sure you have macOS 10.14 or later
2. Try right-clicking the app and selecting "Open" (first time only)
3. Check Console.app for error messages

### Font Issues
- The app uses system fonts for better compatibility
- If you see font warnings, they don't affect functionality

### Background Image Not Showing
- Make sure the image file is in the same directory as the app
- Supported formats: PNG, JPG, JPEG
- The app will fall back to CSS patterns if no image is found

## 📄 License

This project is open source. Feel free to modify and distribute.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

---

**Enjoy your beautiful nighttime to-do list! 🌙✨**
