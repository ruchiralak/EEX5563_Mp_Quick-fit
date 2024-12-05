import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QLineEdit,
    QMessageBox, QWidget, QTableWidget, QTableWidgetItem
)


class QuickFitAllocator:
    def __init__(self):
        self.initial_memory = {
            50: ["Block 1", "Block 2"],
            100: ["Block 3", "Block 4"],
            200: ["Block 5"]
        }
        self.reset()

    def reset(self):
        # Reset memory blocks and allocations to the initial state.
        self.memory = {k: v[:] for k, v in self.initial_memory.items()}
        self.small_blocks = []
        self.allocations = {}

    def allocate(self, process, size):
        # Check if an exact-sized block is available
        exact_block = self._find_exact_block(size)
        if exact_block:
            self.allocations[process] = exact_block
            return f"{process} allocated {size} KB from {exact_block}"

        # Check for the smallest larger block (best-fit approach)
        best_fit_block, remaining = self._find_best_fit_block(size)
        if best_fit_block:
            self.allocations[process] = best_fit_block
            if remaining > 0:
                self.small_blocks.append(f"{remaining} KB from {best_fit_block}")
            return (f"{process} allocated {size} KB from {best_fit_block}. "
                    f"Fragment created: {remaining} KB")

        # No suitable block found
        return f"Allocation failed: No available block can accommodate {size} KB"

    def _find_exact_block(self, size):
        # Find and allocate an exact-sized block if available.
        if size in self.memory and self.memory[size]:
            return self.memory[size].pop(0)
        return None

    def _find_best_fit_block(self, size):
        # Find and allocate the smallest block larger than the requested size.
        for block_size in sorted(self.memory.keys()):
            if block_size > size and self.memory[block_size]:
                block = self.memory[block_size].pop(0)
                return block, block_size - size
        return None, 0

    def display_status(self):
        return {
            "Free Blocks": self.memory,
            "Fragments": self.small_blocks,
            "Allocations": self.allocations
        }


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quick Fit Memory Allocator")
        self.setGeometry(100, 100, 600, 400)

        # Allocator object
        self.allocator = QuickFitAllocator()

        # Layout
        layout = QVBoxLayout()

        # Input field
        self.input_label = QLabel("Enter process size (KB):")
        self.input_field = QLineEdit()
        self.allocate_button = QPushButton("Allocate Memory")
        self.allocate_button.clicked.connect(self.allocate_memory)

        # Clear button
        self.clear_button = QPushButton("Clear All Results")
        self.clear_button.clicked.connect(self.clear_results)

        # Memory status display
        self.status_label = QLabel("Memory Status:")
        self.status_table = QTableWidget(0, 2)
        self.status_table.setHorizontalHeaderLabels(["Category", "Details"])
        self.update_memory_status()

        # Add widgets to layout
        layout.addWidget(self.input_label)
        layout.addWidget(self.input_field)
        layout.addWidget(self.allocate_button)
        layout.addWidget(self.clear_button)
        layout.addWidget(self.status_label)
        layout.addWidget(self.status_table)

        # Set main widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def allocate_memory(self):
        try:
            process_size = int(self.input_field.text())
            process_name = f"Process {len(self.allocator.allocations) + 1}"
            message = self.allocator.allocate(process_name, process_size)
            self.update_memory_status()
            QMessageBox.information(self, "Allocation Result", message)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid integer size.")

    def clear_results(self):
        self.allocator.reset()
        self.update_memory_status()
        QMessageBox.information(self, "Clear Results", "All memory allocations and fragments have been cleared.")

    def update_memory_status(self):
        status = self.allocator.display_status()
        self.status_table.setRowCount(0)
        for category, details in status.items():
            self.status_table.insertRow(self.status_table.rowCount())
            self.status_table.setItem(self.status_table.rowCount() - 1, 0, QTableWidgetItem(category))
            self.status_table.setItem(self.status_table.rowCount() - 1, 1, QTableWidgetItem(str(details)))


# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())