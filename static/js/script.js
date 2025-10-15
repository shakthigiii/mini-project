// static/js/script.js

const questions = []; // Array to hold all question objects
const questionsJsonInput = document.getElementById('questions-json-input');
const addQuestionBtn = document.getElementById('add-question-btn');
const questionListDiv = document.getElementById('question-list');
const questionsAddedCount = document.getElementById('questions-added-count');
const createExamSubmit = document.getElementById('create-exam-submit');
const questionTextarea = document.getElementById('question-text');
const optionInputs = document.querySelectorAll('.opt-input');

// Helper to get the value of the checked radio button (Correct index)
function getCorrectIndex() {
    const radios = document.querySelectorAll('input[name="correctAnswer"]');
    for (let i = 0; i < radios.length; i++) {
        if (radios[i].checked) {
            return radios[i].value;
        }
    }
    return 0; // Default to Option 1 if none is checked
}

// Helper to update the form's hidden JSON field and button state
function updateFormState() {
    questionsJsonInput.value = JSON.stringify(questions);
    questionsAddedCount.innerText = `Questions Added (${questions.length})`;

    if (questions.length > 0) {
        createExamSubmit.disabled = false;
        createExamSubmit.innerText = `Create Exam (${questions.length} questions ready)`;
    } else {
        createExamSubmit.disabled = true;
        createExamSubmit.innerText = `Create Exam (Requires minimum 1 question)`;
    }
    showQuestionList();
}

// Renders the list of added questions
function showQuestionList() {
    questionListDiv.innerHTML = '';
    questions.forEach((q, index) => {
        const div = document.createElement('div');
        div.classList.add('flex', 'items-center', 'justify-between', 'bg-gray-700', 'p-3', 'rounded-lg');
        div.innerHTML = `
            <span class="truncate text-sm">${index + 1}. ${q.description}</span>
            <button type="button" onclick="deleteQuestion(${index})" class="text-red-400 hover:text-red-300">
                <i class="fas fa-trash-alt"></i>
            </button>
        `;
        questionListDiv.appendChild(div);
    });
}

// Deletes a question from the array
function deleteQuestion(index) {
    questions.splice(index, 1);
    updateFormState();
}

// Main event listener for adding a question
addQuestionBtn.addEventListener('click', () => {
    const description = questionTextarea.value.trim();
    const options = Array.from(optionInputs).map(input => input.value.trim());
    const correctIndex = getCorrectIndex();
    const difficulty = document.getElementById('question-difficulty').value;

    if (!description || options.some(opt => opt === "")) {
        alert("Please fill all fields for the question and all four options!");
        return;
    }

    questions.push({
        description: description,
        options: options,
        correct_index: parseInt(correctIndex),
        difficulty: difficulty,
    });

    // Clear form fields
    questionTextarea.value = "";
    optionInputs.forEach(input => input.value = "");
    document.querySelector('input[name="correctAnswer"][value="0"]').checked = true;

    updateFormState();
});

// Attach deleteQuestion function globally so it can be called from innerHTML
window.deleteQuestion = deleteQuestion; 

// Initial state setup
document.addEventListener('DOMContentLoaded', updateFormState);