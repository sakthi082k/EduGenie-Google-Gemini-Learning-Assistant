from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="EduGenie - Google Gemini Powered Learning Assistant")

# Serve CSS and JavaScript files from /static
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

KNOWLEDGE = {
    "photosynthesis": {
        "answer": "Photosynthesis is the process by which green plants make food using sunlight, carbon dioxide and water. Oxygen is released as a by-product.",
        "explain": "Think of a plant as a tiny food factory. Its leaves use sunlight as energy. Carbon dioxide enters from the air and water comes from the roots. The plant uses these to make glucose, and oxygen is released."
    },
    "python": {
        "answer": "Python is a high-level, general-purpose programming language known for readable syntax and a large collection of libraries.",
        "explain": "Python is a programming language that lets us give instructions to a computer. Its syntax is designed to be easy to read, so beginners can learn it comfortably."
    },
    "database": {
        "answer": "A database is an organized collection of data that can be stored, searched, updated and managed efficiently.",
        "explain": "Imagine a digital cupboard with information arranged neatly. A database stores related information so applications can quickly find and update it."
    },
    "sql": {
        "answer": "SQL stands for Structured Query Language. It is commonly used to create, read, update and delete data in relational databases.",
        "explain": "SQL is a language used to communicate with relational databases. You can use it to ask for records, add new records, change existing records and remove records."
    },
    "pythagoras": {
        "answer": "The Pythagorean theorem states that, in a right-angled triangle, a² + b² = c², where c is the hypotenuse.",
        "explain": "For a right-angled triangle, square the two shorter sides and add them. The result equals the square of the longest side, called the hypotenuse."
    }
}

QUIZZES = {
    "python": [
        {"question":"Which keyword is used to define a function in Python?","options":["func","define","def","function"],"answer":"def"},
        {"question":"Which symbol starts a comment in Python?","options":["//","#","<!--","**"],"answer":"#"},
        {"question":"Which data type stores True or False?","options":["String","Boolean","Float","List"],"answer":"Boolean"}
    ],
    "photosynthesis": [
        {"question":"Which gas is used by plants during photosynthesis?","options":["Oxygen","Nitrogen","Carbon dioxide","Hydrogen"],"answer":"Carbon dioxide"},
        {"question":"Where does most photosynthesis occur in a plant?","options":["Roots","Leaves","Flowers","Seeds"],"answer":"Leaves"},
        {"question":"What is the main energy source for photosynthesis?","options":["Moonlight","Sunlight","Wind","Soil"],"answer":"Sunlight"}
    ],
    "database": [
        {"question":"What is a database?","options":["An organized collection of data","A computer cable","A web browser","A programming keyboard"],"answer":"An organized collection of data"},
        {"question":"Which operation adds new data?","options":["INSERT","DELETE","DROP","REMOVE"],"answer":"INSERT"},
        {"question":"What does SQL stand for?","options":["Simple Question Language","Structured Query Language","System Query Link","Standard Quick Language"],"answer":"Structured Query Language"}
    ],
    "pythagoras": [
        {"question":"The Pythagorean theorem is used mainly with which triangle?","options":["Equilateral","Isosceles","Right-angled","Obtuse"],"answer":"Right-angled"},
        {"question":"In a² + b² = c², what is c?","options":["Shortest side","Hypotenuse","Angle","Area"],"answer":"Hypotenuse"},
        {"question":"If a=3 and b=4, what is c?","options":["5","6","7","12"],"answer":"5"}
    ]
}

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())

def local_answer(text: str, explain=False):
    q = normalize(text)
    for key, data in KNOWLEDGE.items():
        if key in q:
            return data["explain"] if explain else data["answer"]
    if "largest ocean" in q:
        return "The Pacific Ocean is the largest ocean on Earth."
    if "water cycle" in q:
        return "The water cycle is the continuous movement of water through evaporation, condensation, precipitation and collection."
    if "machine learning" in q:
        return "Machine learning is a branch of AI in which computers learn patterns from data to make predictions or decisions."
    if explain:
        return "Try a topic such as Python, SQL, databases, photosynthesis, Pythagoras theorem, the water cycle or machine learning."
    return "Try asking about Python, SQL, databases, photosynthesis, Pythagoras theorem, the water cycle or machine learning."

def summarize(text: str):
    text = re.sub(r"\s+", " ", (text or "").strip())
    if not text:
        return "Please enter a passage to summarize."
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    if len(sentences) <= 3:
        return " ".join(sentences)
    return " ".join(dict.fromkeys([sentences[0], sentences[len(sentences)//2], sentences[-1]]))

def recommendations(topic: str):
    topic = (topic or "your topic").strip()
    return (
        f"Learning path for {topic}\\n\\n"
        "1. Beginner: Learn the basic terms and definitions.\\n"
        "2. Practice: Try simple examples and short questions.\\n"
        "3. Intermediate: Explore real-world examples and exercises.\\n"
        "4. Advanced: Build a mini project or solve application-based problems.\\n"
        "5. Revision: Take a quiz, review mistakes and revisit difficult areas.\\n\\n"
        "Suggested resources: class notes, textbooks, trusted documentation and educational videos."
    )

class TextRequest(BaseModel):
    text: str = ""

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request}
    )

@app.post("/qa")
async def qa(data: TextRequest):
    return {"result": local_answer(data.text), "mode": "local"}

@app.post("/explain")
async def explain(data: TextRequest):
    return {"result": local_answer(data.text, explain=True), "mode": "local"}

@app.post("/summarize")
async def summarize_api(data: TextRequest):
    return {"result": summarize(data.text), "mode": "local"}

@app.post("/learn/recommendations")
async def learn(data: TextRequest):
    return {"result": recommendations(data.text), "mode": "local"}

@app.post("/quiz")
async def quiz(data: TextRequest):
    topic = normalize(data.text)
    selected = next((items for key, items in QUIZZES.items() if key in topic or topic in key), None)
    if not selected:
        selected = [
            {"question":f"What is a useful first step when learning {data.text or 'a new topic'}?","options":["Understand the basics","Skip the basics","Avoid practice","Ignore examples"],"answer":"Understand the basics"},
            {"question":"Which activity helps improve learning?","options":["Practice","Never revise","Ignore mistakes","Avoid examples"],"answer":"Practice"},
            {"question":"What should you do after making a mistake?","options":["Review and learn from it","Stop learning","Ignore the topic","Delete your notes"],"answer":"Review and learn from it"}
        ]
    return {"questions": selected, "mode": "local"}

@app.get("/health")
async def health():
    return {"status": "ok", "message": "EduGenie is running locally."}
