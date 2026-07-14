const subject = document.getElementById("subject");
const difficulty = document.getElementById("difficulty");
const questions = document.getElementById("questions");

const generateBtn = document.getElementById("generateBtn");

const setup = document.getElementById("setup");
const quiz = document.getElementById("quiz");

const questionText = document.getElementById("question");
const optionsDiv = document.getElementById("options");

const submitBtn = document.getElementById("submitBtn");
const nextBtn = document.getElementById("nextBtn");

const feedback = document.getElementById("feedback");
const scoreText = document.getElementById("score");

let quizData = [];
let current = 0;
let score = 0;
let selectedAnswer = "";

generateBtn.onclick = async () => {

    const response = await fetch("/generate-quiz", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            subject: subject.value,
            difficulty: difficulty.value,
            questions: parseInt(questions.value)
        })

    });

    const data = await response.json();

    if (data.error) {
        alert(data.error);
        return;
    }

    quizData = data.quiz;

    setup.style.display = "none";
    quiz.style.display = "block";

    current = 0;
    score = 0;

    loadQuestion();
};

function loadQuestion() {

    feedback.innerHTML = "";
    nextBtn.style.display = "none";
    selectedAnswer = "";

    const q = quizData[current];

    questionText.innerHTML =
        `Question ${current + 1}<br><br>${q.question}`;

    optionsDiv.innerHTML = "";

    q.options.forEach(option => {

        const div = document.createElement("div");

        div.className = "option";

        div.innerText = option;

        div.onclick = () => {

            document
                .querySelectorAll(".option")
                .forEach(x => x.classList.remove("selected"));

            div.classList.add("selected");

            selectedAnswer = option;

        };

        optionsDiv.appendChild(div);

    });

}

submitBtn.onclick = () => {

    if (selectedAnswer == "") {

        alert("Select an option");

        return;

    }

    const correct = quizData[current].answer;

    if (selectedAnswer === correct) {

        score++;

        feedback.innerHTML =
            "✅ Correct";

    } else {

        feedback.innerHTML =
            `❌ Wrong<br><br>Correct Answer : <b>${correct}</b>`;

    }

    nextBtn.style.display = "block";

};

nextBtn.onclick = () => {

    current++;

    if (current >= quizData.length) {

        questionText.innerHTML = "🎉 Quiz Finished";

        optionsDiv.innerHTML = "";

        feedback.innerHTML = "";

        submitBtn.style.display = "none";

        nextBtn.style.display = "none";

        scoreText.innerHTML =
            `Final Score : ${score} / ${quizData.length}`;

        return;

    }

    loadQuestion();

};