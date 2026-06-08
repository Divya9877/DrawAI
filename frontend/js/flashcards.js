let cards = [];
let correctAnswer = "";
let score = 0;
let totalQuestions = 0;
let currentIndex = 0;

async function loadCards(){

    try{

        const response = await fetch(

            "http://127.0.0.1:5000/get_flashcards"
        );

        cards = await response.json();

        await showCard();
    }

    catch(error){

        console.error(error);

        document.getElementById(
            "cardTitle"
        ).innerText =
        "Failed to load flashcards";
    }
}
score = parseInt(

    localStorage.getItem(
        "quizScore"
    ) || 0

);

totalQuestions = parseInt(

    localStorage.getItem(
        "quizTotal"
    ) || 0

);

document.getElementById(
    "scoreBoard"
).innerText =

`Score: ${score} / ${totalQuestions}`;

async function showCard(){

    if(cards.length === 0){

        document.getElementById(
            "cardTitle"
        ).innerText =
        "No Flashcards";

        document.getElementById(
            "cardCounter"
        ).innerText =
        "No Cards";

        return;
    }

    const card =
        cards[currentIndex];

    document.getElementById(
        "cardImage"
    ).src =
        card.image;

    document.getElementById(
        "cardTitle"
    ).innerText =
        card.label.toUpperCase();

    document.getElementById(
        "backTitle"
    ).innerText =
        card.label.toUpperCase();

    document.getElementById(
        "cardCounter"
    ).innerText =

        `Card ${currentIndex + 1} of ${cards.length}`;

    document.getElementById(
        "flashcard"
    ).classList.remove(
        "flip"
    );
    document.getElementById(
    "quizSection"
).style.display =
"none";

    try{

        const response = await fetch(

            "http://127.0.0.1:5000/flashcard_explanation",

            {

                method:"POST",

                headers:{
                    "Content-Type":
                    "application/json"
                },

                body:JSON.stringify({

                    label:card.label
                })
            }
        );

       const data =
    await response.json();
    document.getElementById(
    "quizSection"
).style.display =
"block";

document.getElementById(
    "cardDescription"
).innerText =
    data.explanation;

        document.getElementById(
            "cardDescription"
        ).innerText =
            data.explanation;
    }

    catch(error){

        console.error(error);

        document.getElementById(
            "cardDescription"
        ).innerText =

            "Revision notes unavailable.";
    }
}

function flipCard(){

    document.getElementById(
        "flashcard"
    ).classList.toggle(
        "flip"
    );
}

async function nextCard(){

    if(cards.length === 0)
        return;

    currentIndex++;

    if(
        currentIndex >= cards.length
    ){

        currentIndex = 0;
    }

    await showCard();
}

async function previousCard(){

    if(cards.length === 0)
        return;

    currentIndex--;

    if(
        currentIndex < 0
    ){

        currentIndex =
        cards.length - 1;
    }

    await showCard();
}

function goBack(){

    window.location.href =
        "index.html";
}

loadCards();
async function startQuiz(){

    const card =
        cards[currentIndex];

    const response =
        await fetch(

            "http://127.0.0.1:5000/quiz",

            {

                method:"POST",

                headers:{
                    "Content-Type":
                    "application/json"
                },

                body:JSON.stringify({

                    label:
                    card.label
                })
            }
        );

    const data =
        await response.json();

    document.getElementById(
    "quizContainer"
).innerText =
    data.quiz;

   correctAnswer = data.answer;

console.log(correctAnswer);

    document.getElementById(
        "quizResult"
    ).innerHTML = "";
}
function checkAnswer(choice){

    totalQuestions++;

    if(
        choice.toUpperCase() ===
        correctAnswer.toUpperCase()
    ){

        score++;

        document.getElementById(
            "quizResult"
        ).innerHTML =
        "✅ Correct!";

    }

    else{

        document.getElementById(
            "quizResult"
        ).innerHTML =

        `❌ Wrong! Correct Answer: ${correctAnswer}`;
    }

    document.getElementById(
        "scoreBoard"
    ).innerText =

    `Score: ${score} / ${totalQuestions}`;
}
localStorage.setItem(
    "quizScore",
    score
);

localStorage.setItem(
    "quizTotal",
    totalQuestions
);