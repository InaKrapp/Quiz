# A PyQt6 quiz

This is a quiz I developed with PyQt6. Example questions are included in the 'questions' subfolder. Questions can also include images. An example image is included in the 'pictures' subfolder.

The quiz is written in German. It allows the users three different modes to work in:
1. Choosing a category, one or several subcategories. The user is shown all questions in the categories they choose.
2. Repeating marked questions. The user is able to mark questions they wish to repeat later, and all marked questions are shown in this mode.
3. An exam mode: In this mode, the questions shown to the user are choosen randomly and cover all categories.

## Getting started

Before you can run the program, you need to make sure python and the necessary python packages are installed. Python can be downloaded here: [Python](https://www.python.org/downloads/)

### Optional: Set up a virtual environment.
To install the python packages, it is recommended that you create a virtual environment. The code below creates a virtual environment named 'quizvenv'.
  ```sh
python -m venv quizvenv
 ```
Once it is created, you will have to activate it. On the windows powershell, you can do that with the following command:
  ```sh
quizvenv\Scripts\Activate.ps1
 ```

### Install dependencies:
All necessary python packages can be installed at once with the following command:
  ```sh
pip install -r requirements.txt
 ```
Once all dependencies have been successfully installed, you can start the program:
  ```sh
python main.py
 ```
Once the file has started to run, the GUI (graphical user interface) should open. The GUI has been designed to be as self-explanatory as possible.

## Turning the quiz into an exe file
The quiz is designed with the idea in mind to have a program that can be used with a graphical user interface by non-programmers. With pyinstaller, it can easily be turned into an .exe-file that can be opened by clicking on it. Be sure to activate the virtual environment and install the dependencies if you have not done that already. Then, to create the .exe-file, run the following code:
  ```sh
pyinstaller main.spec
 ```
pyinstaller will create two folders, named 'dist' and 'build', in your current directory. You will find the .exe-file in the 'dist' folder. You can run it regardless of where it is on your computer, and also distribute it to other computers, for example, copying it to and from USB flash drives.
