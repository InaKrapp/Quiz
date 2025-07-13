import sys
import os
import json
import random
import Levenshtein
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, 
    QComboBox, QScrollArea, QMessageBox, QButtonGroup, QProgressBar, 
    QSizePolicy, QRadioButton, QHBoxLayout
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from CheckableCombo import MultiComboBox

# Name of question file:
QUESTIONFILE = "test.json"
# Number of random questions to be sampled from each category for the exam:
EXAMQUESTIONNUMBER = 1

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

def add_newline(text, max_length = 80):
    """Adds line breaks to long text to improve readability in the UI"""
    words = text.split()
    if not words:
        return text

    current_length = 0
    new_text = []
    
    # Join words into lines without breaking them
    for word in words:
        if current_length + len(word) > max_length:
            new_text.append('\n')
            current_length = 0
        if current_length > 0:
            new_text.append(' ')
        new_text.append(word)
        current_length += len(word) + (1 if current_length > 0 else 0)
    
    # Handle hyphenated words by ensuring they stay on one line
    new_text = ''.join(new_text).replace('-\n', '-')
    
    return new_text

class Quiz(QWidget):
    """Main quiz application window"""
    
    def __init__(self):
        """Initialize the main quiz window"""
        super().__init__()
        self.initialize_window()
        self.initialize_quiz_state()
        self.create_ui_elements()
        self.configure_ui_layout()
        self.connect_ui_signals()

    def initialize_window(self):
        """Set up basic window properties"""
        self.setWindowTitle("Quiz")
        self.setGeometry(100, 100, 700, 700)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f2f5;
                border-radius: 5px;
                padding: 15px;
            }
            QLabel {
                color: #1a237e;
                font-size: 14pt;
                margin-bottom: 10px;
            }
            QPushButton {
                background-color: #0398c6;
                color: white;
                border: none;
                padding: 10px;
                font-size: 12pt;
                border-radius: 5px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #0398c6;
            }
            QPushButton:pressed {
                background-color: #016c8e;
            }
            QComboBox {
                padding: 5px;
                border-radius: 3px;
                border: 1px solid #ddd;
                font-size: 12pt;
            }
            QRadioButton {
                font-size: 12pt;
                margin-bottom: 5px;
                padding: 3px;
            }
            QProgressBar {
                border-radius: 3px;
                height: 20px;
            }
        """)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

    def initialize_quiz_state(self):
        """Initialize quiz state variables"""
        self.wrong_questions = []
        self.score = 0
        self.current_question = 0
        self.answer_selected = False
        self.questions = []
        self.user_answers = {}  # Dictionary to store selected answers
        self.exam_mode = False
        # Load categories and subcategories
        with open(get_resource_path(f'questions/{QUESTIONFILE}'), 'r', encoding='utf-8') as f:
            data = json.load(f)
        categories = [element.get('category') for element in data]
        self.categories = list(set(categories))
        subcategories = [element.get('subcategory') for element in data]
        self.subcategories = list(set(subcategories))

    def create_ui_elements(self):
        """Create all UI components"""
        self.create_category_selection()
        self.create_start_buttons()
        self.create_scroll_area()
        self.create_progress_bar()

    def configure_ui_layout(self):
        """Configure the layout and visibility of UI elements"""
        header_layout = QVBoxLayout()
        header_layout.addWidget(self.choose_category_label)
        header_layout.addWidget(self.category_combobox)
        
        header_widget = QWidget()
        header_widget.setLayout(header_layout)
        header_widget.setStyleSheet("""
            background-color: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
        """)
        
        self.main_layout.addWidget(header_widget)
        self.main_layout.addWidget(self.category_combo)
        self.main_layout.addWidget(self.start_button)
        self.main_layout.addWidget(self.repeat_marked_questions)
        self.main_layout.addWidget(self.start_exam)
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.progress_bar)

        self.category_combo.hide()
        self.progress_bar.hide()
        self.questions_marked = True
        if not self.questions_marked:
            self.repeat_marked_questions.hide()

    def connect_ui_signals(self):
        """Connect UI components to their respective functions"""
        self.category_combobox.currentTextChanged.connect(self.toggle_subcategory_combo)
        self.start_button.clicked.connect(self.start_quiz)
        self.repeat_marked_questions.clicked.connect(self.repeat_marked_question)
        self.start_exam.clicked.connect(self.create_exam)

    # UI Components

    def create_category_selection(self):
        """Create and configure the category selection UI"""
        self.choose_category_label = QLabel("Wähle das Thema aus, das du üben möchtest. Wähle 'Unterkategorien aussuchen', wenn du bestimmte Unterthemen üben möchtest.")
        self.category_combobox = QComboBox()
        Itemlist = self.categories
        Itemlist.append("Unterkategorien aussuchen")
        self.category_combobox.addItems(
            Itemlist
        )
        
        self.category_combo = MultiComboBox()
        self.category_combo.addItems(self.subcategories)
        self.category_combo.hide()

    def create_start_buttons(self):
        """Creates and configures the buttons shown when the user starts the program."""
        self.start_button = QPushButton("Quiz starten")
        self.repeat_marked_questions = QPushButton("Markierte Fragen wiederholen")
        self.start_exam = QPushButton("Prüfung starten")
        self.start_button.setStyleSheet("""
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #0398c6, stop:1 #00c1ff);
            font-weight: bold;
            min-width: 200px;
        """)
        self.repeat_marked_questions.setStyleSheet("""
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #0398c6, stop:1 #00c1ff);
            font-weight: bold;
            min-width: 200px;
        """)
        self.start_exam.setStyleSheet("""
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #0398c6, stop:1 #00c1ff);
            font-weight: bold;
            min-width: 200px;
        """)
        

    def create_scroll_area(self):
        """Create the scroll area for questions"""
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.container = QWidget()
        self.container.setLayout(QVBoxLayout())
        self.scroll_area.setWidget(self.container)

    def create_progress_bar(self):
        """Create and configure the progress bar"""
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar { 
                background-color: #e3f2fd; 
                border-radius: 3px; 
                text-align: center; 
                font-size: 10pt;
            } 
            QProgressBar::chunk { 
                background-color: #0398c6; 
            }
        """)

    # Quiz Logic

    def toggle_subcategory_combo(self, text):
        """Show/hide subcategory combo based on selection"""
        self.category_combo.setVisible(text == "Unterkategorien aussuchen")

    def start_quiz(self):
        """Start the quiz with selected categories"""
        selected_categories = self.get_selected_categories()
        if not selected_categories:
            return
        # Load questions and initialize quiz state
        self.questions = self.load_questions(selected_categories)
        if not self.questions:
            return

        self.initialize_quiz()
        self.show_question()

    def get_selected_categories(self):
        """Get selected categories from UI"""
        main_category = self.category_combobox.currentText()
        return main_category if main_category != "Unterkategorien aussuchen" else self.category_combo.currentText()

    def load_questions(self, categories):
        """Load questions a JSON file based on selected categories:
        Reads a JSON file and keeps only entries where 'category' or 'subcategory' contains the target_str.
        """
        with open(get_resource_path(f'questions/{QUESTIONFILE}'), 'r', encoding='utf-8') as f:
            data = json.load(f)

        filtered_data = []
        for entry in data:
            category = entry.get('category', '')
            subcategory = entry.get('subcategory', '')
            # Check if the target string is present in either category or subcategory
            if category in categories or subcategory in categories:
                filtered_data.append(entry)
        return filtered_data

    def format_questions(self, questions):
        """Add line breaks to questions and answers"""
        return [
            {
                **q,
                'question': add_newline(q['question']),
                'options': [add_newline(opt) for opt in q['options']],
                'correct': add_newline(q['correct'])
            }
            for q in questions
        ]

    def initialize_quiz(self):
        """Initialize quiz state and UI"""
        self.current_question = 0
        self.score = 0
        self.wrong_questions.clear()
        self.answer_selected = False

        # Hide category selection
        self.choose_category_label.hide()
        self.category_combobox.hide()
        self.category_combo.hide()
        self.start_button.hide()
        self.repeat_marked_questions.hide()
        self.start_exam.hide()

        # Show progress bar
        self.progress_bar.show()
        self.progress_bar.setMaximum(len(self.questions))
        self.progress_bar.setValue(0)


    def show_question(self):
        """Display the current question"""
        # Clear previous question
        self.clear_question_container()

        # Get current question
        question = self.questions[self.current_question]

        # Add question components
        self.add_question_text(question)
        self.add_question_image(question.get("image", None))
        self.add_answer_options(question["options"])
        self.add_next_button()

    def clear_question_container(self):
        """Clear all widgets from the question container"""
        for i in reversed(range(self.container.layout().count())): 
            widget = self.container.layout().takeAt(i).widget()
            if widget is not None: 
                widget.deleteLater()

    def add_question_text(self, question):
        """Add the question text to the container"""
        category = question["category"]
        subcategory = question["subcategory"]
        category_label = QLabel(f"{category} - {subcategory}")
        question_label = QLabel(question["question"])
        question_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        category_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        question_label.setWordWrap(True)
        category_label.setWordWrap(True)
        question_label.setStyleSheet("""
            background-color: white;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 15px;
        """)
        category_label.setStyleSheet("""
            padding: 5px;
            border-radius: 5px;
            margin-bottom: 5px;
        """)
        self.container.layout().addWidget(category_label)
        self.container.layout().addWidget(question_label)

    def add_question_image(self, image_path):
        """Add an image to the question container, scaled to a consistent size."""
        MAX_IMAGE_WIDTH = 800  # Maximum width for images
        MAX_IMAGE_HEIGHT = 450  # Maximum height for images
        ZOOM_FACTOR = 0.8      # Optional: Adjust this to zoom in or out
        if image_path:
            image_path = get_resource_path(image_path)
            try:
                image = QImage()
                if image.load(image_path):
                    pixmap = QPixmap.fromImage(image)

                    # Calculate scaling factor based on MAX dimensions
                    original_width = pixmap.width()
                    original_height = pixmap.height()
                    
                    # Scale factor to ensure the image fits within MAX dimensions
                    scale_factor = min(
                        MAX_IMAGE_WIDTH / original_width,
                        MAX_IMAGE_HEIGHT / original_height
                    )

                    # Optional: Apply a zoom factor (optional adjustment)
                    scale_factor = scale_factor * ZOOM_FACTOR

                    scaled_width = int(original_width * scale_factor)
                    scaled_height = int(original_height * scale_factor)

                    # Scale the pixmap while preserving aspect ratio
                    scaled_pixmap = pixmap.scaled(
                        scaled_width,
                        scaled_height,
                        Qt.AspectRatioMode.KeepAspectRatio
                    )

                    # Create a label to display the scaled pixmap
                    image_label = QLabel()
                    image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    image_label.setPixmap(scaled_pixmap)
                    image_label.setStyleSheet("""
                        background-color: white;
                        padding: 10px;
                        border-radius: 5px;
                        margin: 15px 0;
                    """)
                    image_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                    # Add to the container
                    self.container.layout().addWidget(image_label)

            except Exception as e:
                print(f"Error loading image: {e}")


    def add_answer_options(self, options):
        """Create and add answer options to the container"""
        answer_group = QButtonGroup()
        answer_group.setExclusive(True)
        
        for option in options:
            option = add_newline(option, max_length = 140)
            button = QRadioButton(option)
            button.setStyleSheet("""
                QRadioButton {
                    background-color: white;
                    padding: 10px;
                    margin: 5px 0;
                    border: 1px solid #ddd;
                    border-radius: 3px;              
                    white-space: pre-wrap; 
                }
                QRadioButton:hover {
                    background-color: #f5f5f5;
                }
                QRadioButton:checked {
                    background-color: #d3f1ff;
                    border-color: #0398c6;
                }
            """)
            button.clicked.connect(lambda: self.store_answer())
            answer_group.addButton(button)
            self.container.layout().addWidget(button)
        self.answer_group = answer_group
        self.answer_group.setObjectName("radioGroup")

    def store_answer(self):
        """Check if the selected answer is correct"""
        self.answer_selected = True
        question = self.questions[self.current_question]
        questions = question['options']
        correct_answer = question["correct"]
        main_category = question['category']

        # Get answer chosen by the user:
        button = self.sender()
        if button.isChecked():
            selected_answer = button.text()

        # Store the selected answer for evaluation later
        self.user_answers[self.current_question] = {
            'question': question['question'],
            'selected': selected_answer,
            'correct': question['correct'],
            'options':question['options'],
            'main_category':main_category
        }

    def add_next_button(self):
        """Add next button to the container"""
        if self.current_question < len(self.questions) - 1:
            button_text = "Nächste Frage"
            next_action = self.next_question
        else:
            button_text = "Quiz beenden"
            next_action = self.finish_quiz

        button_container = QWidget()
        button_container.setLayout(QHBoxLayout())

        # Add previous button
        if self.current_question > 0:
            previous_button = QPushButton("Zurück zur vorherigen Frage")
            previous_button.setStyleSheet("""
                QPushButton {
                    background-color: #73c2ff;
                    padding: 10px;
                    margin-right: 10px;
                }
                QPushButton:hover {
                    background-color: #2ECCFA;
                }
            """)
            previous_button.clicked.connect(self.previous_question)
        else:
            previous_button = None  # Don't show a previous button on first question
        self.mark_button = QPushButton("Frage markieren" if self.questions[self.current_question]["marked"] == False else "Frage aus markierten Fragen entfernen")
        self.mark_button.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                padding: 10px;
                margin-right: 10px;
            }
            QPushButton:hover {
                background-color: #ff5252;
            }
        """)
        self.mark_button.clicked.connect(self.mark_question)

        next_button = QPushButton(button_text)
        next_button.setStyleSheet("""
            QPushButton {
                background-color: #73c2ff;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2ECCFA;
            }
        """)
        next_button.clicked.connect(next_action)

        if previous_button:
            button_container.layout().addWidget(previous_button)
        button_container.layout().addWidget(self.mark_button)
        button_container.layout().addWidget(next_button)

        self.container.layout().addWidget(button_container)

    def next_question(self):
        """Move to the next question"""
        if not self.answer_selected:
            if self.current_question not in self.wrong_questions:
                self.wrong_questions.append(self.current_question)

        self.answer_selected = False
        self.progress_bar.setValue(self.current_question + 1)
        self.current_question += 1
        self.show_question()

    def previous_question(self):
        """Move to previous question. If the user selected an answer for that question already, click on it again."""
        # Move current question index and progress bar status to that of the previous question:
        self.current_question -= 1
        self.progress_bar.setValue(self.current_question - 1)
        self.show_question()
        # If the user had clicked on an answer, display this click to the user again:
        for button in self.answer_group.buttons():
            try:
                if button.text() == self.user_answers[self.current_question]['selected']:
                    button.click()  # Simulates the button click
            except KeyError: # If the user selected no answer, no button needs to be clicked.
                pass

    def finish_quiz(self):
        """End the quiz and show results"""
        # Reset evaluation state
        self.score = 0
        self.wrong_questions.clear()
        if self.exam_mode == True:
            for j in self.categories:
                questionlist = []
                len_questions = 0
                self.score = 0
                for i in range(len(self.questions)):
                    if j in self.user_answers[i]['main_category']:
                        len_questions = len_questions + 1
                        if i in self.user_answers:
                            selected = self.user_answers[i]['selected']
                            correct = self.user_answers[i]['correct']
                            options = self.user_answers[i]['options']
                            distance_to_A = Levenshtein.distance(selected, correct)
                            distances_to_others = [Levenshtein.distance(selected, s) for s in options if s != correct]
                            answer_true = all(distance_to_A < d for d in distances_to_others)

                            if answer_true:
                                self.score += 1
                            else:
                                self.wrong_questions.append(i)
                            questionlist.append(self.user_answers[i])
                        # Show results
                total_questions = len_questions
                try:
                    score_percentage = (self.score / total_questions) * 100

                    if score_percentage >= 75:
                        endtext = f"Quiz in Kategorie {j} erfolgreich abgeschlossen! \nHerzlichen Glückwunsch!"
                    else:
                        endtext = f"Quiz in Kategorie {j} leider nicht bestanden. \nBeim nächsten Mal klappt's bestimmt besser!"


                    result_msg = (
                                f"{endtext}\n\n"
                                f"Ergebnis: {self.score}/{total_questions}\n"
                                f"Prozentuale Bewertung: {score_percentage:.1f}%"
                        )
                                    # Show result message and ask to repeat wrong answers
                    if score_percentage >= 75:
                        QMessageBox.information(self, "Quiz beendet.", result_msg)
                    else:
                        QMessageBox.information(self, "Quiz beendet.",  result_msg)
                except ZeroDivisionError:
                    pass
            # End exam mode:
            self.exam_mode = False
            self.back_to_menu()
        else:
            # Compare all answers and calculate results
            for i in range(len(self.questions)):
                if i in self.user_answers:
                    selected = self.user_answers[i]['selected']
                    correct = self.user_answers[i]['correct']
                    options = self.user_answers[i]['options']
                    distance_to_A = Levenshtein.distance(selected, correct)
                    distances_to_others = [Levenshtein.distance(selected, s) for s in options if s != correct]
                    answer_true = all(distance_to_A < d for d in distances_to_others)

                    if answer_true:
                        self.score += 1
                    else:
                        self.wrong_questions.append(i)
                else:
                    # If no answer was selected, mark the question as wrong
                    self.wrong_questions.append(i)

            # Show results
            total_questions = len(self.questions)
            score_percentage = (self.score / total_questions) * 100

            if score_percentage >= 75:
                endtext = "Quiz erfolgreich abgeschlossen! \nHerzlichen Glückwunsch!"
            else:
                endtext = "Quiz leider nicht bestanden. \nBeim nächsten Mal klappt's bestimmt besser!"

            result_msg = (
                f"{endtext}\n\n"
                f"Ergebnis: {self.score}/{total_questions}\n"
                f"Prozentuale Bewertung: {score_percentage:.1f}%"
            )

            # Reset user answers for next quiz
            self.user_answers.clear()

            # Show result message and ask to repeat wrong answers
            if score_percentage >= 75:
                QMessageBox.information(self, "Quiz beendet.", result_msg)
            else:
                QMessageBox.information(self, "Quiz beendet.",  result_msg)

            if self.wrong_questions:
                repeat = QMessageBox.question(
                    self,
                    "Wiederholung",
                    "Möchtest du die falsch oder nicht beantworteten Fragen noch einmal versuchen?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if repeat == QMessageBox.StandardButton.Yes:
                    self.repeat_wrong_questions()
                    return

            self.back_to_menu()

    def repeat_wrong_questions(self):
        """Repeat questions that were answered incorrectly"""
        self.questions = [self.questions[i] for i in self.wrong_questions]
        self.wrong_questions.clear()
        self.score = 0
        self.current_question = 0
        self.progress_bar.setMaximum(len(self.questions))
        self.progress_bar.setValue(0)
        self.show_question()

    def get_marked_questions(self):
        """Helper function to load marked questions from JSON"""
        try:
            with open(get_resource_path(f'questions/{QUESTIONFILE}'), 'r', encoding='utf-8') as file:
                questions =  json.load(file)
                filtered_questions = [entry for entry in questions if entry["marked"] == True]
                return filtered_questions

        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def mark_question(self):
        """Implement method to mark questions if the user wants to repeat them later."""
        # Load all questions from the JSON file
        with open(get_resource_path(f'questions/{QUESTIONFILE}'), 'r', encoding='utf-8') as file:
            all_questions = json.load(file)

        # Get current question
        question = self.questions[self.current_question]

        # Find the index of the question 'question' in 'all_questions'.
        for i, element in enumerate(all_questions):
            if element["question"] ==  question['question']:
                current_index = i

        for i, question in enumerate(all_questions):
            if i == current_index:
                question["marked"] = not question["marked"]
                break
        
        # Update button text based on new status
        if all_questions[current_index]["marked"]:
            self.mark_button.setText("Frage aus markierten Fragen entfernen")
        else:
            self.mark_button.setText("Frage markieren")
        
        # Save the updated questions back to the JSON file
        with open(get_resource_path(f'questions/{QUESTIONFILE}'), 'w', encoding='utf-8') as file:
            json.dump(all_questions, file, ensure_ascii=False, indent=4)

    def repeat_marked_question(self):
        """Implement method to repeat marked questions."""
        # Check if json file exists and contains questions. If not, give message: 'Keine Fragen markiert.'
        try:
            with open(get_resource_path(f'questions/{QUESTIONFILE}'), 'r', encoding='UTF-8') as f:
                category_questions = json.load(f)
                filtered_questions = [entry for entry in category_questions if entry["marked"] == True]
                #formatted_questions = self.format_questions(filtered_questions)
                # Disable formatting for now:
                formatted_questions = filtered_questions
                if not formatted_questions:
                    self.info()
                    return
                self.questions = formatted_questions
                self.initialize_quiz()
                self.wrong_questions.clear()
                self.score = 0
                self.current_question = 0
                self.show_question()
        except FileNotFoundError:
            self.info()

    def create_exam(self):
        """ An exam contains questions choosen randomly from each section.
        For each section, the user gets informed if they passed or not."""
        # Load questions and initialize quiz state
        self.exam_mode = True

        # Load categories and subcategories
        with open(get_resource_path(f'questions/{QUESTIONFILE}'), 'r', encoding='utf-8') as f:
            data = json.load(f)
        categories = [element.get('category') for element in data]
        self.categories = list(set(categories))
        subcategories = [element.get('subcategory') for element in data]
        self.subcategories = list(set(subcategories))

        questionlist = []
        # Choose random questions from each category:
        for category in self.categories:
            questions = self.load_questions(category)
            questions = random.sample(questions, EXAMQUESTIONNUMBER)
            questionlist.extend(questions)
        self.questions = questionlist
        self.initialize_quiz()
        self.show_question()

    
    def info(self):
        QMessageBox.information(
            self,
            'Keine Fragen markiert.',
            'Markiere Fragen, um sie zu wiederholen.'
        )

    def back_to_menu(self):
        """Return to the main menu"""
        self.wrong_questions.clear()
        self.score = 0
        self.current_question = 0
        self.questions.clear()

        # Clear question container
        self.clear_question_container()

        # Show category selection
        self.choose_category_label.show()
        self.category_combobox.show()
        self.start_button.show()
        self.repeat_marked_questions.show()
        if self.category_combobox.currentText() == "Unterkategorien aussuchen":
            self.category_combo.show()
        self.start_exam.show()
        self.progress_bar.hide()

    def __del__(self):
        """Clean up resources when widget is destroyed"""
        self.clear_question_container()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet('* { font-size: 12pt;}')
    quiz = Quiz()
    quiz.show()
    sys.exit(app.exec())