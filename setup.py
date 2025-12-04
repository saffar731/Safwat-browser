import sys
import os
import json
import uuid # For generating anonymous user IDs
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QLineEdit, QAction, QStatusBar, 
    QVBoxLayout, QWidget, QTabWidget, QSplitter, QPushButton, QHBoxLayout,
    QDialog, QGridLayout, QLabel, QGroupBox, QRadioButton, QMessageBox, 
    QSizePolicy, QSpacerItem
)
from PyQt5.QtWebEngineWidgets import QWebEngineView

# --- ENVIRONMENT & FIREBASE CONTEXT (MANDATORY GLOBALS) ---
# NOTE: In this simulated environment, these globals would be provided at runtime.
# We use mock values to allow the Python code to run standalone and demonstrate state management.
try:
    # Attempt to load real global variables if available
    appId = __app_id if '__app_id' in globals() else 'mock-app-id'
    
    if '__firebase_config' in globals():
        firebaseConfig = json.loads(__firebase_config) if __firebase_config else {}
    else:
        firebaseConfig = {}
    
    initialAuthToken = __initial_auth_token if '__initial_auth_token' in globals() else None
except NameError:
    # Use mock values for local testing/standalone execution
    appId = 'mock-app-id'
    firebaseConfig = {}
    initialAuthToken = "mock-custom-auth-token-12345"  # Simulate a user being signed in initially

# --- Configuration ---
DEFAULT_URL = "https://search.brave.com/"
DEFAULT_ZOOM = 0.75

# Fixed Quick Links (Icon: URL)
FIXED_QUICK_LINKS = {
    "Search 🔎": "https://www.google.com",
    "Code </>": "https://github.com",
    "Help 💡": "https://stackoverflow.com",
    "News 📰": "https://news.ycombinator.com"
}

# --- THEME DEFINITIONS ---
DARK_THEME_CSS = """
    QMainWindow { background-color: #2e2e2e; color: #ffffff; font-family: Inter, Arial, sans-serif; }
    QToolBar { background: #3c3c3c; border: 1px solid #555555; border-radius: 6px; margin: 5px; spacing: 5px; }
    QAction { color: #ffffff; }
    QStatusBar { background: #3c3c3c; color: #cccccc; }
    QLineEdit { background: #555555; color: #ffffff; padding: 5px; border: 1px solid #777777; border-radius: 4px; }
    QToolButton { padding: 5px; border-radius: 5px; margin: 2px; color: #ffffff; font-size: 16px; }
    QToolButton:hover { background: #555555; }
    
    QTabBar::tab { background: #444444; color: #ffffff; padding: 8px 15px; border-top-left-radius: 6px; border-top-right-radius: 6px; border: 1px solid #555555; border-bottom: none; margin-right: 2px; }
    QTabBar::tab:selected { background: #2e2e2e; border-color: #555555; border-bottom-color: #2e2e2e; }
    
    QPushButton { background: #5a5a5a; color: white; border: 1px solid #777; padding: 5px 10px; border-radius: 4px; }
    QPushButton:hover { background: #6b6b6b; }
    
    #GameButton { background: #ff5555; color: white; font-weight: bold; border: none; padding: 5px 15px; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.5); }
    #GameButton:hover { background: #e04444; }
    
    QDialog { background-color: #3c3c3c; color: #ffffff; }
    QGroupBox { border: 1px solid #555555; margin-top: 10px; }
    QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 3px; color: #ffffff; }
    QLabel { color: #ffffff; }
    
    QWebEngineView { background-color: #1e1e1e; }
"""

LIGHT_THEME_CSS = """
    QMainWindow { background-color: #f0f0f0; color: #000000; font-family: Inter, Arial, sans-serif; }
    QToolBar { background: #ffffff; border: 1px solid #cccccc; border-radius: 6px; margin: 5px; spacing: 5px; }
    QAction { color: #000000; }
    QStatusBar { background: #ffffff; color: #333333; }
    QLineEdit { background: #ffffff; color: #000000; padding: 5px; border: 1px solid #cccccc; border-radius: 4px; }
    QToolButton { padding: 5px; border-radius: 5px; margin: 2px; color: #000000; font-size: 16px; }
    QToolButton:hover { background: #e0e0e0; }
    
    QTabBar::tab { background: #e0e0e0; color: #000000; padding: 8px 15px; border-top-left-radius: 6px; border-top-right-radius: 6px; border: 1px solid #cccccc; border-bottom: none; margin-right: 2px; }
    QTabBar::tab:selected { background: #f0f0f0; border-color: #cccccc; border-bottom-color: #f0f0f0; }
    
    QPushButton { background: #cccccc; color: black; border: 1px solid #aaaaaa; padding: 5px 10px; border-radius: 4px; }
    QPushButton:hover { background: #bbbbbb; }
    
    #GameButton { background: #ff7777; color: white; font-weight: bold; border: none; padding: 5px 15px; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
    #GameButton:hover { background: #f06666; }
    
    QDialog { background-color: #ffffff; color: #000000; }
    QGroupBox { border: 1px solid #cccccc; margin-top: 10px; }
    QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 3px; color: #000000; }
    QLabel { color: #000000; }
    
    QWebEngineView { background-color: #ffffff; }
"""

# --- OFFLINE GAME CONTENT (HTML/JS) ---
FLAPPY_BIRD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Flappy Bird Offline</title>
    <style>
        body { margin: 0; display: flex; justify-content: center; align-items: center; background-color: #333; height: 100vh; font-family: 'Inter', sans-serif; user-select: none; }
        .game-container { text-align: center; }
        .message { color: #fff; margin-bottom: 20px; font-size: 1.2rem; }
        .controls { color: #ccc; margin-top: 10px; font-size: 0.9rem; }
        #gameCanvas { 
            background: linear-gradient(to bottom, #70c5ce 0%, #b8e9f0 100%); 
            border: 4px solid #555; 
            border-radius: 8px; 
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.5); 
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="game-container">
        <div class="message">
            <span style="color: #ff5555; font-weight: bold;">NETWORK OFFLINE!</span><br>
            Flap to pass the time!
        </div>
        <canvas id="gameCanvas" width="320" height="480"></canvas>
        <div class="controls">
            Press SPACE or CLICK to FLAP
        </div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        const BIRD_SIZE = 25;
        const PIPE_WIDTH = 52;
        const PIPE_GAP = 100;
        const GROUND_HEIGHT = 40;
        const SPEED = 2; 

        let bird = { x: 50, y: canvas.height / 2, velocity: 0, gravity: 0.2, jump: -4.5 };
        let pipes = [];
        let score = 0;
        let isGameOver = false;
        let isGameStarted = false;
        let animationFrameId;
        let pipeTimer = 0;
        const PIPE_SPAWN_INTERVAL = 150; 

        function addPipe() {
            let topPipeHeight = Math.random() * (canvas.height - PIPE_GAP - GROUND_HEIGHT - 100) + 50;
            pipes.push({ x: canvas.width, y: 0, width: PIPE_WIDTH, height: topPipeHeight, scored: false });
            pipes.push({ x: canvas.width, y: topPipeHeight + PIPE_GAP, width: PIPE_WIDTH, height: canvas.height - topPipeHeight - PIPE_GAP - GROUND_HEIGHT, scored: false });
        }

        function drawBird() {
            ctx.fillStyle = '#ffde00'; 
            ctx.beginPath();
            ctx.arc(bird.x, bird.y, BIRD_SIZE / 2, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = '#000';
            ctx.lineWidth = 2;
            ctx.stroke();
            ctx.fillStyle = 'black';
            ctx.beginPath();
            ctx.arc(bird.x + BIRD_SIZE / 4, bird.y - BIRD_SIZE / 8, 3, 0, Math.PI * 2);
            ctx.fill();
        }

        function drawPipes() {
            ctx.fillStyle = '#7ac70c'; 
            ctx.strokeStyle = '#387309'; 
            ctx.lineWidth = 2;

            pipes.forEach(p => {
                ctx.fillRect(p.x, p.y, p.width, p.height);
                ctx.strokeRect(p.x, p.y, p.width, p.height);

                ctx.fillStyle = '#a6e344'; 
                if (p.y === 0) {
                    ctx.fillRect(p.x - 5, p.height - 15, p.width + 10, 15);
                    ctx.strokeRect(p.x - 5, p.height - 15, p.width + 10, 15);
                } else {
                    ctx.fillRect(p.x - 5, p.y, p.width + 10, 15);
                    ctx.strokeRect(p.x - 5, p.y, p.width + 10, 15);
                }
            });
        }
        
        function drawGround() {
            ctx.fillStyle = '#ded895'; 
            ctx.fillRect(0, canvas.height - GROUND_HEIGHT, canvas.width, GROUND_HEIGHT);
            ctx.strokeStyle = '#8b7c41';
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(0, canvas.height - GROUND_HEIGHT);
            ctx.lineTo(canvas.width, canvas.height - GROUND_HEIGHT);
            ctx.stroke();
        }
        
        function drawScore() {
            ctx.fillStyle = 'white';
            ctx.strokeStyle = 'black';
            ctx.lineWidth = 3;
            ctx.font = '36px "Inter", sans-serif';
            ctx.textAlign = 'center';
            ctx.strokeText(score, canvas.width / 2, 50);
            ctx.fillText(score, canvas.width / 2, 50);
        }
        
        function drawStartScreen() {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.4)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = 'white';
            ctx.font = '24px "Inter", sans-serif';
            ctx.fillText('Click or Spacebar to Start', canvas.width / 2, canvas.height / 2 - 20);
            ctx.font = '16px "Inter", sans-serif';
            ctx.fillText('Best Score: ' + (localStorage.getItem('flappyHighScore') || 0), canvas.width / 2, canvas.height / 2 + 20);
        }

        function drawGameOver() {
            let highScore = localStorage.getItem('flappyHighScore') || 0;
            if (score > highScore) {
                highScore = score;
                localStorage.setItem('flappyHighScore', score);
            }

            ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#ff5555';
            ctx.font = '48px "Inter", sans-serif';
            ctx.fillText('GAME OVER', canvas.width / 2, canvas.height / 2 - 40);
            
            ctx.fillStyle = 'white';
            ctx.font = '24px "Inter", sans-serif';
            ctx.fillText('Score: ' + score, canvas.width / 2, canvas.height / 2 + 10);
            ctx.fillText('High Score: ' + highScore, canvas.width / 2, canvas.height / 2 + 50);
            
            ctx.font = '18px "Inter", sans-serif';
            ctx.fillText('Click or Spacebar to Restart', canvas.width / 2, canvas.height / 2 + 100);
        }

        function collision(p) {
            const birdTop = bird.y - BIRD_SIZE / 2;
            const birdBottom = bird.y + BIRD_SIZE / 2;
            const birdLeft = bird.x - BIRD_SIZE / 2;
            const birdRight = bird.x + BIRD_SIZE / 2;

            const pipeCollides = (
                birdRight > p.x && 
                birdLeft < p.x + p.width && 
                birdBottom > p.y && 
                birdTop < p.y + p.height
            );

            const boundaryCollides = birdBottom >= canvas.height - GROUND_HEIGHT || birdTop <= 0;

            return pipeCollides || boundaryCollides;
        }

        function flap() {
            if (isGameOver) {
                resetGame();
            } else if (!isGameStarted) {
                isGameStarted = true;
                bird.velocity = bird.jump;
            } else {
                bird.velocity = bird.jump;
            }
        }
        
        function resetGame() {
            bird = { x: 50, y: canvas.height / 2, velocity: 0, gravity: 0.2, jump: -4.5 };
            pipes = [];
            score = 0;
            isGameOver = false;
            isGameStarted = false; 
            pipeTimer = 0;
            
            if (animationFrameId) cancelAnimationFrame(animationFrameId);
            gameLoop();
        }

        function updateGame() {
            if (!isGameStarted || isGameOver) return;
            
            bird.velocity += bird.gravity;
            bird.y += bird.velocity;

            pipeTimer++;
            if (pipeTimer > PIPE_SPAWN_INTERVAL) {
                addPipe();
                pipeTimer = 0;
            }

            for (let i = pipes.length - 1; i >= 0; i--) {
                let p = pipes[i];
                p.x -= SPEED;

                if (collision(p)) {
                    isGameOver = true;
                    cancelAnimationFrame(animationFrameId);
                    drawGameOver();
                    return;
                }

                if (i % 2 === 0 && !p.scored && p.x + p.width < bird.x - BIRD_SIZE / 2) {
                    score++;
                    p.scored = true;
                }

                if (i % 2 === 0 && p.x + p.width < 0) {
                    pipes.splice(i, 2); 
                }
            }
        }

        function gameLoop() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            drawGround();
            drawPipes();
            drawBird();
            drawScore();
            
            updateGame();

            if (!isGameStarted && !isGameOver) {
                drawStartScreen();
            } else if (isGameOver) {
                drawGameOver();
            }

            if (!isGameOver) {
                animationFrameId = requestAnimationFrame(gameLoop);
            }
        }

        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space') {
                e.preventDefault();
                flap();
            }
        });
        canvas.addEventListener('click', flap);
        canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            flap();
        });

        gameLoop(); 
    </script>
</body>
</html>
"""

class TabContent(QWidget):
    """Container widget for QWebEngineView."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.browser = QWebEngineView()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.browser)

class SettingsDialog(QDialog):
    """Dialog for browser settings (Login and Theme)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings ⚙️")
        self.browser_window = parent
        self.setup_ui()
        self.resize(400, 300)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)

        # 1. User Authentication Group 
        auth_group = QGroupBox("User Authentication (Firebase Mock)")
        auth_layout = QVBoxLayout(auth_group)
        
        self.status_label = QLabel()
        self.update_auth_status_label()
        auth_layout.addWidget(self.status_label)
        
        self.auth_btn_layout = QHBoxLayout()
        self.sign_in_btn = QPushButton("Sign In Anonymously")
        self.sign_out_btn = QPushButton("Sign Out")
        
        self.sign_in_btn.clicked.connect(self.handle_sign_in)
        self.sign_out_btn.clicked.connect(self.handle_sign_out)

        self.auth_btn_layout.addWidget(self.sign_in_btn)
        self.auth_btn_layout.addWidget(self.sign_out_btn)
        auth_layout.addLayout(self.auth_btn_layout)
        
        main_layout.addWidget(auth_group)

        # 2. Theme Selection Group
        theme_group = QGroupBox("Browser Theme")
        theme_layout = QVBoxLayout(theme_group)
        
        self.radio_dark = QRadioButton("Dark Theme (Default)")
        self.radio_light = QRadioButton("Light Theme")
        
        current_theme = self.browser_window.current_theme
        if current_theme == 'dark':
            self.radio_dark.setChecked(True)
        else:
            self.radio_light.setChecked(True)

        self.radio_dark.toggled.connect(lambda: self.apply_setting('dark') if self.radio_dark.isChecked() else None)
        self.radio_light.toggled.connect(lambda: self.apply_setting('light') if self.radio_light.isChecked() else None)

        theme_layout.addWidget(self.radio_dark)
        theme_layout.addWidget(self.radio_light)
        main_layout.addWidget(theme_group)
        
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        main_layout.addWidget(close_btn)

        self.update_button_visibility()

    def update_auth_status_label(self):
        """Updates the status label based on the BrowserWindow's current auth state."""
        if self.browser_window.is_authenticated:
            # Display the full user ID as required for multi-user apps
            status_text = f"Status: Logged In\nUser ID: {self.browser_window.user_id}"
            self.status_label.setStyleSheet("color: #7ac70c;")
        else:
            status_text = "Status: Logged Out (Anonymous Mode)"
            self.status_label.setStyleSheet("color: #ff5555;")
        self.status_label.setText(status_text)
        
    def update_button_visibility(self):
        """Manages which auth buttons are visible."""
        is_auth = self.browser_window.is_authenticated
        self.sign_in_btn.setVisible(not is_auth)
        self.sign_out_btn.setVisible(is_auth)

    def handle_sign_in(self):
        """Simulates successful Firebase Anonymous Sign In."""
        self.browser_window.sign_in_anonymously()
        self.update_auth_status_label()
        self.update_button_visibility()
        QMessageBox.information(self, "Login Success", "Successfully signed in anonymously (simulated Firebase process).")

    def handle_sign_out(self):
        """Simulates successful Firebase Sign Out."""
        self.browser_window.sign_out_user()
        self.update_auth_status_label()
        self.update_button_visibility()
        QMessageBox.information(self, "Logout Success", "Successfully signed out (simulated Firebase process).")

    def apply_setting(self, theme):
        """Applies the theme setting."""
        if self.browser_window:
            self.browser_window.apply_theme(theme)


class AddLinkDialog(QDialog):
    """Dialog for adding a new Quick Link."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Quick Link ➕")
        self.link_name = None
        self.link_url = None
        self.setup_ui()

    def setup_ui(self):
        layout = QGridLayout(self)
        self.name_input = QLineEdit()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com (must start with http/https)")
        
        layout.addWidget(QLabel("Icon/Name:"), 0, 0)
        layout.addWidget(self.name_input, 0, 1)
        layout.addWidget(QLabel("URL:"), 1, 0)
        layout.addWidget(self.url_input, 1, 1)

        ok_button = QPushButton("Add Link")
        ok_button.clicked.connect(self.validate_and_accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout, 2, 0, 1, 2)
        
    def validate_and_accept(self):
        name = self.name_input.text().strip()
        url = self.url_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Input Error", "Please enter a name/icon for the link.")
            return
        if not url or not (url.startswith('http://') or url.startswith('https://')):
            QMessageBox.warning(self, "Input Error", "Please enter a valid URL starting with http:// or https://.")
            return

        self.link_name = name
        self.link_url = url
        self.accept()


class BrowserWindow(QMainWindow):
    """
    The main window for the Web Developer Browser application, featuring tabs,
    integrated DevTools, custom themes, and user-configurable quick links,
    and simulated Firebase authentication.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Safwat Browser")
        self.setGeometry(100, 100, 1000, 700) 
        
        # Internal state for quick links, theme, and authentication
        self.custom_quick_links = {}
        self.current_theme = 'dark' 
        self.is_authenticated = False
        self.user_id = None
        
        # 1. Initialize Authentication State
        self._initialize_auth_state()

        # 2. Central Widget and Layout setup
        main_container = QWidget()
        self.main_layout = QVBoxLayout(main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(main_container)
        
        # 3. Setup Toolbar
        self._setup_toolbar()
        
        # 4. Tab Widget & Dev Tools (QSplitter)
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab) 
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        
        self.dev_tools_view = QWebEngineView()
        self.dev_tools_view.hide()
        
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(self.tabs)
        self.splitter.addWidget(self.dev_tools_view)
        self.splitter.setSizes([1000, 0]) 
        
        self.main_layout.addWidget(self.splitter)
        
        # 5. Setup Bottom Controls
        self._setup_bottom_controls()
        
        # 6. Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 7. Apply initial theme
        self.apply_theme(self.current_theme)

        # 8. Initial Tab
        self.add_new_tab(QUrl(DEFAULT_URL), "Homepage")
    
    def _initialize_auth_state(self):
        """
        Simulates Firebase Auth Initialization: 
        Attempts to sign in using the provided custom token (__initial_auth_token).
        """
        if initialAuthToken:
            # Simulate successful signInWithCustomToken and retrieve user ID
            # In a real setup, this token exchange would happen via Firebase Auth SDK
            try:
                # Mock a fixed UID associated with the custom token for demonstration
                self.user_id = "initial-user-" + str(uuid.uuid4())[:8] 
                self.is_authenticated = True
                print(f"Auth initialized: Signed in with token, UID: {self.user_id}")
            except Exception as e:
                # Fallback to anonymous if token fails
                self.sign_in_anonymously()
        else:
            # If no initial token, sign in anonymously by default
            self.sign_in_anonymously()

    def sign_in_anonymously(self):
        """Simulates Firebase signInAnonymously."""
        # In a real app, this would use the Firebase JS/Python SDK.
        # We mock a successful sign-in with a new, random UID.
        self.user_id = "anon-" + str(uuid.uuid4())
        self.is_authenticated = True
        print(f"Auth: Signed in anonymously, UID: {self.user_id}")

    def sign_out_user(self):
        """Simulates Firebase signOut."""
        # In a real app, this would use the Firebase JS/Python SDK.
        self.user_id = None
        self.is_authenticated = False
        print("Auth: Signed out.")

    def current_browser(self):
        """Helper to get the QWebEngineView of the currently active tab."""
        current_tab_widget = self.tabs.currentWidget()
        return current_tab_widget.browser if current_tab_widget else None

    def close_current_tab(self, index):
        """Closes the specified tab."""
        if self.tabs.count() < 2:
            return
        
        widget = self.tabs.widget(index)
        widget.deleteLater()
        self.tabs.removeTab(index)

    def apply_theme(self, theme_name):
        """Applies the selected theme CSS globally."""
        self.current_theme = theme_name
        css = DARK_THEME_CSS if theme_name == 'dark' else LIGHT_THEME_CSS
        QApplication.instance().setStyleSheet(css)

    def add_new_tab(self, qurl=None, label="New Tab"):
        """Adds a new tab with a QWebEngineView."""
        tab_widget = TabContent(self)
        browser = tab_widget.browser
        
        browser.setZoomFactor(DEFAULT_ZOOM)
        
        if qurl:
            browser.setUrl(qurl)
        
        browser.urlChanged.connect(lambda url: self.update_url_bar(url) if browser == self.current_browser() else None)
        browser.loadStarted.connect(lambda: self.setStatusTip("Loading...") if browser == self.current_browser() else None)
        browser.loadFinished.connect(lambda success: self.on_load_finished(success, browser, tab_widget))
        browser.titleChanged.connect(lambda title: self.tabs.setTabText(self.tabs.indexOf(tab_widget), title))

        i = self.tabs.addTab(tab_widget, label)
        self.tabs.setCurrentIndex(i)

        if self.tabs.count() == 1:
            self.current_tab_changed(i)

    def on_load_finished(self, success, browser, tab_widget):
        """If loading fails (simulated network error), loads the Flappy Bird game."""
        if browser == self.current_browser():
            self.setStatusTip("Done" if success else "Load Failed")
            self.update_url_bar(browser.url())
        
        if not success:
            if browser.url().toString() != 'qrc:/offline_game':
                self.load_flappy_bird_game()
            else:
                self.setStatusTip("Critical Error: Cannot Load Game or Network.")
        else:
            if browser.zoomFactor() != DEFAULT_ZOOM and browser.url().toString() != 'qrc:/offline_game':
                 browser.setZoomFactor(DEFAULT_ZOOM)

    def navigate_to_quick_link(self, url):
        """Navigates the current browser tab to the provided quick link URL."""
        browser = self.current_browser()
        if browser:
            browser.setUrl(QUrl(url))
            
    def load_flappy_bird_game(self):
        """Loads the Flappy Bird game directly into the current tab."""
        browser = self.current_browser()
        if browser:
            browser.setHtml(FLAPPY_BIRD_HTML, QUrl('qrc:/offline_game'))
            browser.setZoomFactor(1.0) 
            
            current_tab_widget = self.tabs.currentWidget()
            if current_tab_widget:
                self.tabs.setTabText(self.tabs.indexOf(current_tab_widget), "Flappy Bird 🐦")
                self.setStatusTip("Playing Flappy Bird")
            
    def _setup_bottom_controls(self):
        """Sets up the Quick Links bar and the dedicated game button."""
        
        self.bottom_widget = QWidget()
        self.bottom_layout = QHBoxLayout(self.bottom_widget)
        self.bottom_layout.setContentsMargins(10, 5, 10, 5)
        self.main_layout.addWidget(self.bottom_widget)
        
        self._render_quick_apps()
    
    def _render_quick_apps(self):
        """Renders/re-renders all quick link buttons in the bottom bar."""
        
        for i in reversed(range(self.bottom_layout.count())): 
            item = self.bottom_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
            else:
                self.bottom_layout.removeItem(item)
            
        # 1. Add FIXED Quick Links
        all_links = {**FIXED_QUICK_LINKS, **self.custom_quick_links}
        
        for name, url in all_links.items():
            link_btn = QPushButton(name)
            link_btn.setToolTip(url) 
            link_btn.clicked.connect(lambda checked, target_url=url: self.navigate_to_quick_link(target_url))
            self.bottom_layout.addWidget(link_btn)

        # 2. Add Link Button
        add_link_btn = QPushButton("➕ Add Link")
        add_link_btn.clicked.connect(self.prompt_add_quick_link)
        self.bottom_layout.addWidget(add_link_btn)

        # 3. Add a spacer to push the game button to the right
        self.bottom_layout.addStretch()

        # 4. Start Flappy Bird Button
        game_btn = QPushButton("Start Flappy Bird 🐦")
        game_btn.setObjectName("GameButton") 
        game_btn.clicked.connect(self.load_flappy_bird_game)
        self.bottom_layout.addWidget(game_btn)

    def prompt_add_quick_link(self):
        """Opens the dialog to get details for a new quick link."""
        dialog = AddLinkDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name = dialog.link_name
            url = dialog.link_url
            
            self.custom_quick_links[name] = url
            self._render_quick_apps() 

    def _setup_toolbar(self):
        """Creates and configures the navigation, tab, and settings toolbar."""
        nav_toolbar = QToolBar("Navigation")
        self.addToolBar(nav_toolbar)
        
        # Navigation Buttons (Icons only)
        back_btn = QAction("←", self); back_btn.triggered.connect(lambda: self.current_browser().back()); back_btn.setToolTip("Back")
        forward_btn = QAction("→", self); forward_btn.triggered.connect(lambda: self.current_browser().forward()); forward_btn.setToolTip("Forward")
        reload_btn = QAction("↻", self); reload_btn.triggered.connect(lambda: self.current_browser().reload()); reload_btn.setToolTip("Reload")
        stop_btn = QAction("🛑", self); stop_btn.triggered.connect(lambda: self.current_browser().stop()); stop_btn.setToolTip("Stop")
        
        nav_toolbar.addAction(back_btn)
        nav_toolbar.addAction(forward_btn)
        nav_toolbar.addAction(reload_btn)
        nav_toolbar.addAction(stop_btn)
        
        # New Tab Button
        new_tab_btn = QAction("➕", self)
        new_tab_btn.setToolTip("Open a new tab")
        new_tab_btn.triggered.connect(lambda: self.add_new_tab(QUrl(DEFAULT_URL)))
        nav_toolbar.addAction(new_tab_btn)

        # URL Bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_toolbar.addWidget(self.url_bar)
        
        # DevTools Button (Inspect)
        self.dev_tools_btn = QAction("🔍", self)
        self.dev_tools_btn.setToolTip("Toggle integrated developer tools (Inspect)")
        self.dev_tools_btn.triggered.connect(self.open_dev_tools)
        nav_toolbar.addAction(self.dev_tools_btn)

        # Settings Button
        settings_btn = QAction("⚙️", self)
        settings_btn.setToolTip("Browser Settings and Theme")
        settings_btn.triggered.connect(self.open_settings)
        nav_toolbar.addAction(settings_btn)
    
    def current_tab_changed(self, index):
        """Updates UI elements when the active tab changes."""
        browser = self.current_browser()
        if browser:
            self.update_url_bar(browser.url())
            self.setWindowTitle(browser.title() or "Safwat Browser")
            
            if not self.dev_tools_view.isHidden():
                browser.page().setDevToolsPage(self.dev_tools_view.page())

    def open_settings(self):
        """Opens the Settings dialog."""
        # Pass self (BrowserWindow) as parent to the dialog so it can access auth/theme state
        dialog = SettingsDialog(self)
        dialog.exec_()

    def navigate_to_url(self):
        """Handles URL navigation and search."""
        url_text = self.url_bar.text().strip()
        
        if not url_text: return

        if os.path.exists(url_text):
            qurl = QUrl.fromLocalFile(url_text)
        elif url_text.startswith(('http://', 'https://', 'file://', 'qrc://')):
            qurl = QUrl(url_text)
        elif ' ' in url_text:
            qurl = QUrl(f"https://search.brave.com/search?q={url_text}")
        else:
            qurl = QUrl(f"https://{url_text}")
        
        browser = self.current_browser()
        if browser:
            browser.setUrl(qurl)

    def update_url_bar(self, url):
        """Updates the URL bar with the currently loaded URL."""
        if self.current_browser():
            self.url_bar.setText(url.toString())
            self.url_bar.setCursorPosition(0)
        
    def open_dev_tools(self):
        """Toggles the integrated Developer Tools view."""
        browser = self.current_browser()
        if not browser: return

        if self.dev_tools_view.isHidden():
            browser.page().setDevToolsPage(self.dev_tools_view.page())
            self.dev_tools_view.show()
            self.splitter.setSizes([700, 300]) 
            self.dev_tools_btn.setText("❌")
            self.dev_tools_btn.setToolTip("Close Developer Tools")
        else:
            self.dev_tools_view.hide()
            self.splitter.setSizes([1000, 0])
            self.dev_tools_btn.setText("🔍")
            self.dev_tools_btn.setToolTip("Toggle integrated developer tools (Inspect)")
            browser.page().setDevToolsPage(None)


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    
    window = BrowserWindow()
    window.show()
    
    sys.exit(app.exec_())