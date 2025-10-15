// Function to start the quiz timer
function startTimer(durationMinutes) {
    let timeLeft = durationMinutes * 60;
    const timerElement = document.getElementById('timer');

    const timer = setInterval(() => {
        if (timeLeft <= 0) {
            clearInterval(timer);
            alert('Time is up! The quiz will now be submitted.');
            document.getElementById('quiz-form').submit();
        } else {
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            timerElement.innerText = `Time Left: ${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
            timeLeft--;
        }
    }, 1000);
}

// Function to handle tab switching
function setupTabSwitchingDetection() {
    let warnings = 0;
    const maxWarnings = 2;

    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'hidden') {
            warnings++;
            if (warnings >= maxWarnings) {
                alert('Warning: You have switched tabs too many times. The quiz will be submitted.');
                document.getElementById('quiz-form').submit();
            } else {
                alert(`Warning ${warnings}/${maxWarnings}: Tab switching is not allowed. Further attempts will result in quiz submission.`);
            }
        }
    });
}

// Disable copy and paste
function disableCopyPaste() {
    document.addEventListener('copy', (e) => e.preventDefault());
    document.addEventListener('paste', (e) => e.preventDefault());
    document.addEventListener('contextmenu', (e) => e.preventDefault());
}

// Run functions when the page loads
function setupBeforeUnload() {
    window.addEventListener('beforeunload', function(e) {
        // This message is often ignored by modern browsers, but the action still occurs.
        e.preventDefault();
        e.returnValue = ''; 
        // Automatically submit the quiz form
        document.getElementById('quiz-form').submit();
    });
}

// Update your onload function
window.onload = function() {
    startTimer(quizDuration);
    setupTabSwitchingDetection();
    disableCopyPaste();
    setupBeforeUnload(); // Add this new function
};

// quiz.js
// (Your existing functions)

