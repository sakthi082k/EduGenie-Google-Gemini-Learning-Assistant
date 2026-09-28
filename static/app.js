const tasks = {
  qa: {title:"Ask a Question", desc:"Enter an academic question and get a concise answer.", placeholder:"Example: Which is the largest ocean?"},
  explain: {title:"Explain a Topic", desc:"Get a simple, student-friendly explanation.", placeholder:"Example: Explain photosynthesis in simple words."},
  quiz: {title:"Generate Quiz", desc:"Generate multiple-choice questions and check your answers.", placeholder:"Example: Python"},
  summarize: {title:"Summarize Text", desc:"Turn a long passage into a short revision-friendly summary.", placeholder:"Paste your educational paragraph here..."},
  learn: {title:"Learning Path", desc:"Get a structured beginner-to-advanced learning plan.", placeholder:"Example: SQL"}
};
let currentTask = "qa";
const taskButtons = document.querySelectorAll(".task");
const titleBox = document.getElementById("taskTitle");
const input = document.getElementById("inputText");
const result = document.getElementById("result");
const loader = document.getElementById("loader");

taskButtons.forEach(button => button.addEventListener("click", () => {
  taskButtons.forEach(item => item.classList.remove("active"));
  button.classList.add("active");
  currentTask = button.dataset.task;
  titleBox.innerHTML = `<h2>${tasks[currentTask].title}</h2><p>${tasks[currentTask].desc}</p>`;
  input.placeholder = tasks[currentTask].placeholder;
  result.classList.add("hidden");
  result.innerHTML = "";
}));

document.getElementById("clearBtn").addEventListener("click", () => {
  input.value = "";
  result.classList.add("hidden");
  result.innerHTML = "";
  input.focus();
});

document.getElementById("runBtn").addEventListener("click", async () => {
  const text = input.value.trim();
  if (!text) { alert("Please enter some text first."); input.focus(); return; }
  loader.classList.remove("hidden");
  result.classList.add("hidden");
  const endpoint = currentTask === "learn" ? "/learn/recommendations" : `/${currentTask}`;
  try {
    const response = await fetch(endpoint, {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({text})
    });
    if (!response.ok) throw new Error("Request failed");
    const data = await response.json();
    loader.classList.add("hidden");
    if (currentTask === "quiz") showQuiz(data.questions || []);
    else { result.textContent = data.result || "No result received."; result.classList.remove("hidden"); }
  } catch (error) {
    loader.classList.add("hidden");
    result.textContent = "Could not connect to EduGenie. Check that the FastAPI server is running in VS Code.";
    result.classList.remove("hidden");
  }
});

function showQuiz(questions) {
  result.innerHTML = "<h3>Your practice quiz</h3>";
  let score = 0, answered = 0;
  questions.forEach((question, index) => {
    const card = document.createElement("div");
    card.className = "quiz-card";
    const prompt = document.createElement("strong");
    prompt.textContent = `${index + 1}. ${question.question}`;
    card.appendChild(prompt);
    question.options.forEach(option => {
      const button = document.createElement("button");
      button.className = "option";
      button.textContent = option;
      button.addEventListener("click", () => {
        if (card.dataset.done) return;
        card.dataset.done = "true";
        answered++;
        if (option === question.answer) { button.classList.add("correct"); score++; }
        else {
          button.classList.add("wrong");
          card.querySelectorAll(".option").forEach(item => {
            if (item.textContent === question.answer) item.classList.add("correct");
          });
        }
        if (answered === questions.length) {
          const scoreBox = document.createElement("div");
          scoreBox.className = "score";
          scoreBox.textContent = `Your score: ${score} / ${questions.length}`;
          result.appendChild(scoreBox);
        }
      });
      card.appendChild(button);
    });
    result.appendChild(card);
  });
  result.classList.remove("hidden");
}
