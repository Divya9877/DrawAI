/* =========================================
   CANVAS
========================================= */

const canvas =
document.getElementById(
    "drawingCanvas"
);

const ctx =
canvas.getContext("2d");

/* =========================================
   RESPONSIVE CANVAS FIX
========================================= */

function resizeCanvas(){

    const rect =
        canvas.getBoundingClientRect();

    canvas.width =
        rect.width;

    canvas.height =
        rect.height;

    ctx.fillStyle =
        "#0f172a";

    ctx.fillRect(

        0,
        0,

        canvas.width,
        canvas.height
    );

    ctx.lineWidth = 6;

    ctx.lineCap = "round";

    ctx.lineJoin = "round";

    ctx.strokeStyle = "white";
}

resizeCanvas();

window.addEventListener(
    "resize",
    resizeCanvas
);

/* =========================================
   DRAW VARIABLES
========================================= */

let drawing = false;

let erasing = false;

let lastLabel = "";

/* =========================================
   GET CORRECT POINTER POSITION
========================================= */

function getMousePos(e){

    const rect =
        canvas.getBoundingClientRect();

    return {

        x:

        (e.clientX - rect.left) *

        (canvas.width / rect.width),

        y:

        (e.clientY - rect.top) *

        (canvas.height / rect.height)
    };
}

/* =========================================
   START DRAWING
========================================= */

function startDrawing(e){

    drawing = true;

    const pos =
        getMousePos(e);

    ctx.beginPath();

    ctx.moveTo(
        pos.x,
        pos.y
    );
}

/* =========================================
   STOP DRAWING
========================================= */

function stopDrawing(){

    drawing = false;

    ctx.beginPath();
}

/* =========================================
   DRAW
========================================= */

function draw(e){

    if(!drawing) return;

    const pos =
        getMousePos(e);

    ctx.strokeStyle =

        erasing

        ? "#0f172a"

        : "white";

    ctx.lineTo(
        pos.x,
        pos.y
    );

    ctx.stroke();

    ctx.beginPath();

    ctx.moveTo(
        pos.x,
        pos.y
    );
}

/* =========================================
   EVENTS
========================================= */

canvas.addEventListener(
    "mousedown",
    startDrawing
);

canvas.addEventListener(
    "mouseup",
    stopDrawing
);

canvas.addEventListener(
    "mouseleave",
    stopDrawing
);

canvas.addEventListener(
    "mousemove",
    draw
);

/* =========================================
   TOUCH SUPPORT
========================================= */

canvas.addEventListener(

    "touchstart",

    (e)=>{

        e.preventDefault();

        const touch =
            e.touches[0];

        startDrawing({

            clientX: touch.clientX,

            clientY: touch.clientY
        });
    }
);

canvas.addEventListener(

    "touchmove",

    (e)=>{

        e.preventDefault();

        const touch =
            e.touches[0];

        draw({

            clientX: touch.clientX,

            clientY: touch.clientY
        });
    }
);

canvas.addEventListener(
    "touchend",
    stopDrawing
);

/* =========================================
   TOOL BUTTONS
========================================= */

function setPencil(){

    erasing = false;
}

function setEraser(){

    erasing =
     true;
}

function clearBoard(){

    ctx.fillStyle =
        "#0f172a";

    ctx.fillRect(

        0,
        0,

        canvas.width,
        canvas.height
    );

    document.getElementById(
        "predictionBox"
    ).innerHTML = "";

    document.getElementById(
        "chatMessages"
    ).innerHTML = "";

    lastLabel = "";
}

/* =========================================
   PREDICT
========================================= */

async function predictDrawing(){

    try{

        const imageData =
            canvas.toDataURL(
                "image/png"
            );

        const response = await fetch(

            "http://127.0.0.1:5000/predict",

            {

                method:"POST",

                headers:{
                    "Content-Type":
                    "application/json"
                },

                body:JSON.stringify({

                    image:imageData
                })
            }
        );

        const data =
            await response.json();

        // Save label

        lastLabel =
            data.label;

        localStorage.setItem(

            "lastLabel",

            data.label
        );

        // Show prediction

        document.getElementById(

            "predictionBox"

        ).innerHTML =

        `
        <h3>
            Prediction:
            ${data.label}
        </h3>

        <p>
            Confidence:
            ${data.confidence}%
        </p>
        `;

        // Save prediction for restore

        localStorage.setItem(

            "predictionBox",

            document.getElementById(
                "predictionBox"
            ).innerHTML
        );

        // Save canvas

        localStorage.setItem(

            "savedCanvas",

            canvas.toDataURL()
        );

        getExplanation(
            data.label
        );
    }

    catch(error){

        console.error(error);

        alert(
            "Prediction failed"
        );
    }
}

/* =========================================
   EXPLANATION
========================================= */

async function getExplanation(label){

    try{

        const response = await fetch(

            "http://127.0.0.1:5000/confirm",

            {

                method:"POST",

                headers:{
                    "Content-Type":
                    "application/json"
                },

                body:JSON.stringify({

                    label:label
                })
            }
        );

        const data =
            await response.json();

        document.getElementById(

            "chatMessages"

        ).innerHTML +=

        `<p>
        <b>AI:</b>
        ${data.info}
        </p>`;
        localStorage.setItem(
    "explanation",
    data.info
);
    }

    catch(error){

        console.error(error);
    }
}

/* =========================================
   GENERATE 3D
========================================= */

async function open3D(){

    try{

        const imageData =
            canvas.toDataURL(
                "image/png"
            );

        const response = await fetch(

            "http://127.0.0.1:5000/generate_3d",

            {

                method:"POST",

                headers:{
                    "Content-Type":
                    "application/json"
                },

                body:JSON.stringify({

                    image:imageData
                })
            }
        );

        const data =
            await response.json();

        console.log(data);

        if(

            data.success &&

            data.model
        ){
           localStorage.setItem(
    "savedCanvas",
    canvas.toDataURL()
);

saveConversation();
            window.location.href =

                "viewer.html?model=" +

                encodeURIComponent(
                    data.model
                );
        }

        else{

            alert(
                "3D generation failed"
            );
        }
    }

    catch(error){

        console.error(error);

        alert(
            "3D generation failed"
        );
    }
}

/* =========================================
   SPEAK
========================================= */

let speechUtterance = null;

function speakExplanation(){

    const text =

        document.getElementById(
            "chatMessages"
        ).innerText;

    if(!text) return;

    window.speechSynthesis.cancel();

    speechUtterance =

        new SpeechSynthesisUtterance(
            text
        );

    window.speechSynthesis.speak(
        speechUtterance
    );
}

function stopSpeaking(){

    window.speechSynthesis.cancel();

    speechUtterance = null;
}

/* =========================================
   CHAT
========================================= */

async function sendMessage(){

    const input =
        document.getElementById(
            "chatInput"
        );

    const message =
        input.value.trim();

    if(!message) return;
    saveChat(message);

    input.value = "";

    const chatMessages =
        document.getElementById(
            "chatMessages"
        );

    // USER MESSAGE

    chatMessages.innerHTML +=

    `<div class="user-bubble">
        ${message}
    </div>`;


    try{

        const response = await fetch(

            "http://127.0.0.1:5000/chat",

            {

                method:"POST",

                headers:{
                    "Content-Type":
                    "application/json"
                },

                body:JSON.stringify({

                    message:message,

                    label:lastLabel
                })
            }
        );

        const data =
            await response.json();

        // AI MESSAGE

        chatMessages.innerHTML +=

        `<div class="ai-bubble">
            ${data.reply}
        </div>`;
        saveConversation();

        chatMessages.scrollTop =
            chatMessages.scrollHeight;

    }

    catch(error){

        console.error(error);
    }
}

/* =========================================
   IMAGE UPLOAD
========================================= */

document.getElementById(

    "uploadInput"

).addEventListener(

    "change",

    function(event){

        const file =
            event.target.files[0];

        if(!file) return;

        const reader =
            new FileReader();

        reader.onload =
        function(e){

            const img =
                new Image();

            img.onload =
            function(){

                ctx.drawImage(

                    img,

                    0,
                    0,

                    canvas.width,
                    canvas.height
                );
            };

            img.src =
                e.target.result;
        };

        reader.readAsDataURL(
            file
        );
    }
);

/* =========================================
   VOICE CHAT
========================================= */

function startVoiceChat(){

    const SpeechRecognition =

        window.SpeechRecognition ||

        window.webkitSpeechRecognition;

    if(!SpeechRecognition){

        alert(
            "Speech recognition is not supported in this browser."
        );

        return;
    }

    const recognition =
        new SpeechRecognition();

    recognition.lang = "en-US";

    recognition.continuous = false;

    recognition.interimResults = false;

    recognition.start();

    recognition.onstart = function(){

        console.log(
            "Listening..."
        );
    };

    recognition.onresult = function(event){

        const transcript =

            event.results[0][0].transcript;

        document.getElementById(
            "chatInput"
        ).value = transcript;

        sendMessage();
    };


    recognition.onerror = function(event){

        console.error(
            event.error
        );

        alert(
            "Voice recognition failed."
        );
    };
}

function openFlashcards(){

    localStorage.setItem(
        "savedCanvas",
        canvas.toDataURL()
    );

    saveConversation();

    window.location.href =
        "flashcards.html";
}
function logout(){

    localStorage.removeItem(
        "user_id"
    );

    localStorage.removeItem(
        "user_name"
    );

    window.location.href =
        "login.html";
}

function openDashboard(){

    localStorage.setItem(

        "savedCanvas",

        canvas.toDataURL()
    );

    saveConversation();

    window.location.href =
        "dashboard.html";
}

function saveChat(message){

    const userId =

        localStorage.getItem(
            "user_id"
        );

    const key =

        `recentChats_${userId}`;

    let chats =

        JSON.parse(

            localStorage.getItem(
                key
            )

        ) || [];

    if(!chats.includes(message)){

        chats.unshift(message);
    }

    localStorage.setItem(

        key,

        JSON.stringify(chats)
    );

    loadRecentChats();
}

function loadRecentChats(){

    const userId =

        localStorage.getItem(
            "user_id"
        );

    const key =

        `recentChats_${userId}`;

    const chats =

        JSON.parse(

            localStorage.getItem(
                key
            )

        ) || [];

    let html = "";

    chats.forEach(chat => {

        html += `

        <div class="chat-history-item">

            ${chat}

        </div>

        `;
    });

    document.getElementById(
        "chatHistory"
    ).innerHTML =
    html;
}

function loadConversation(){

    const userId =

        localStorage.getItem(
            "user_id"
        );

    const oldChat =

        localStorage.getItem(

            `conversation_${userId}`

        );

    if(oldChat){

        document.getElementById(

            "chatMessages"

        ).innerHTML = oldChat;
    }
}
function newChat(){

    document.getElementById(
        "chatMessages"
    ).innerHTML = "";
}
