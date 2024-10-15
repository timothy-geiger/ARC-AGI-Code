""" With the help of
https://www.kaggle.com/code/allegich/arc-2024-starter-notebook-eda
"""

import json
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.colors import ListedColormap, Normalize
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


# Apply global settings for text color
mpl.rcParams["text.color"] = "white"
mpl.rcParams["axes.labelcolor"] = "white"
mpl.rcParams["xtick.color"] = "white"
mpl.rcParams["ytick.color"] = "white"
mpl.rcParams["axes.titlecolor"] = "white"


class PuzzleViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        # Define window
        self.setWindowTitle("Puzzle Viewer")
        self.setGeometry(100, 100, 800, 600)

        # Define the paths
        self.base_path = "./data/"
        self.training_path = self.base_path + "training/"
        self.evaluation_path = self.base_path + "evaluation/"
        self.test_path = self.base_path + "test/"

        # Load data
        self.training_challenges = self.load_json(
            self.training_path + "arc-agi_training_challenges.json"
        )
        self.training_solutions = self.load_json(
            self.training_path + "arc-agi_training_solutions.json"
        )
        self.evaluation_challenges = self.load_json(
            self.evaluation_path + "arc-agi_evaluation_challenges.json"
        )
        self.evaluation_solutions = self.load_json(
            self.evaluation_path + "arc-agi_evaluation_solutions.json"
        )
        self.test_challenges = self.load_json(
            self.test_path + "arc-agi_test_challenges.json"
        )

        # Custom colormap and normalization
        self.cmap = ListedColormap(
            [
                "#000000",
                "#0074D9",
                "#FF4136",
                "#2ECC40",
                "#FFDC00",
                "#AAAAAA",
                "#F012BE",
                "#FF851B",
                "#7FDBFF",
                "#870C25",
            ]
        )
        self.norm = Normalize(vmin=0, vmax=9)

        # Current puzzle index
        self.current_index = 0
        self.current_set = []
        self.current_solutions = []

        # Main widget
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        # Layout
        layout = QVBoxLayout(self.main_widget)

        # Heading layout
        heading_layout = QHBoxLayout()

        # Heading label
        self.heading_label = QLabel(self)
        self.heading_label.setAlignment(Qt.AlignCenter)
        heading_layout.addWidget(self.heading_label)

        # Copy button
        self.copy_button = QPushButton("Copy Name")
        self.copy_button.clicked.connect(self.copy_name_to_clipboard)
        heading_layout.addWidget(self.copy_button)

        layout.addLayout(heading_layout)

        # Dropdown for selecting data set
        self.set_dropdown = QComboBox(self)
        self.set_dropdown.addItems(["Train", "Test", "Evaluation"])
        self.set_dropdown.currentIndexChanged.connect(self.on_set_change)
        layout.addWidget(self.set_dropdown)

        # Puzzle display area
        self.figure = plt.figure()
        self.figure.patch.set_facecolor("None")
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color:transparent;")
        layout.addWidget(self.canvas)

        # Buttons for navigation
        button_layout = QHBoxLayout()

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.show_previous)
        button_layout.addWidget(self.back_button)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.show_next)
        button_layout.addWidget(self.next_button)

        layout.addLayout(button_layout)

        # Search functionality
        search_layout = QHBoxLayout()

        self.search_input = QLineEdit(self)
        search_layout.addWidget(QLabel("Search Puzzle #:"))
        search_layout.addWidget(self.search_input)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_puzzle)
        search_layout.addWidget(self.search_button)

        self.search_input.returnPressed.connect(self.search_puzzle)

        layout.addLayout(search_layout)

        # Initial set load
        self.on_set_change()

    def copy_name_to_clipboard(self):
        """Copies the current puzzle name to the clipboard."""
        current_name = self.current_set[self.current_index][0]
        clipboard = QApplication.clipboard()
        clipboard.setText(current_name)

    def load_json(self, filepath):
        """Loads JSON data from the specified filepath."""
        with open(filepath, "r") as file:
            return json.load(file)

    def plot_one(self, ax, i, train_or_test, input_or_output, task):
        input_matrix = task[train_or_test][i][input_or_output]
        ax.imshow(input_matrix, cmap=self.cmap, norm=self.norm)
        ax.grid(True, which="both", color="lightgrey", linewidth=0.5)

        plt.setp(plt.gcf().get_axes(), xticklabels=[], yticklabels=[])
        ax.set_xticks([x - 0.5 for x in range(len(input_matrix[0]) + 1)])
        ax.set_yticks([x - 0.5 for x in range(len(input_matrix) + 1)])

        ax.set_title(f"""
            {train_or_test.capitalize()} {input_or_output.capitalize()}
        """)

    def plot_task(self, task, task_solutions, t):
        """Plots the task using the provided layout on the canvas"""
        num_train = len(task["train"])
        num_test = len(task["test"])
        w = num_train + num_test

        # Update subtitle label
        self.heading_label.setText(f"Set #{self.current_index + 1}, {t}:")
        self.canvas.figure.clear()

        # Create subplots using add_subplot
        axs = []

        for j in range(2):  # 2 rows
            row = []

            for k in range(w):  # w columns
                ax = self.canvas.figure.add_subplot(2, w, j * w + k + 1)
                row.append(ax)

            axs.append(row)

        for j in range(num_train):
            self.plot_one(axs[0][j], j, "train", "input", task)
            self.plot_one(axs[1][j], j, "train", "output", task)

        # Test input and solution
        self.plot_one(axs[0][num_train], 0, "test", "input", task)

        axs[1][num_train].imshow(
            task_solutions, cmap=self.cmap, norm=self.norm)

        axs[1][num_train].grid(
            True, which="both", color="lightgrey", linewidth=0.5)

        axs[1][num_train].set_xticks(
            [x - 0.5 for x in range(len(task_solutions[0]) + 1)]
        )

        axs[1][num_train].set_yticks(
            [x - 0.5 for x in range(len(task_solutions) + 1)])

        axs[1][num_train].set_xticklabels([])
        axs[1][num_train].set_yticklabels([])
        axs[1][num_train].set_title("Test Output")

        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def on_set_change(self):
        """Handles set selection from dropdown."""
        set_choice = self.set_dropdown.currentText()

        if set_choice == "Train":
            self.current_set = list(self.training_challenges.items())
            self.current_solutions = list(self.training_solutions.items())

        elif set_choice == "Test":
            self.current_set = list(self.test_challenges.items())
            self.current_solutions = []

        elif set_choice == "Evaluation":
            self.current_set = list(self.evaluation_challenges.items())
            self.current_solutions = list(self.evaluation_solutions.items())

        self.current_index = 0
        self.show_puzzle()

    def show_puzzle(self):
        """Displays the current puzzle using the
        provided plot_task function."""
        if not self.current_set:
            QMessageBox.warning(self, "Error", "No puzzles available.")
            return

        task = self.current_set[self.current_index][1]
        t = self.current_set[self.current_index][0]
        task_solution = None

        if self.current_solutions:
            task_solution = self.current_solutions[self.current_index][1][0]

        # Plot the puzzle on the embedded canvas
        self.plot_task(task, task_solution, t)

    def show_next(self):
        """Shows the next puzzle."""
        if self.current_index < len(self.current_set)-1:
            self.current_index += 1

        else:
            # Go to first (cycle)
            self.current_index = 0

        self.show_puzzle()

    def show_previous(self):
        """Shows the previous puzzle."""
        if self.current_index > 0:
            self.current_index -= 1

        else:
            # Go to last (cycle)
            self.current_index = len(self.current_set)-1

        self.show_puzzle()

    def search_puzzle(self):
        puzzle_name = self.search_input.text().strip()
        found = False

        for index, (name, _) in enumerate(self.current_set):
            if name.lower() == puzzle_name.lower():
                self.current_index = index
                self.show_puzzle()
                found = True
                break

        if not found:
            QMessageBox.warning(
                self, "Not Found", "Puzzle name not found in the current set."
            )


# Main function
def main():
    app = QApplication(sys.argv)
    viewer = PuzzleViewer()
    viewer.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
