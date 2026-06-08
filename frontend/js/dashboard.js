async function loadDashboard(){

    const response =
        await fetch(
            "http://127.0.0.1:5000/dashboard"
        );

    const data =
        await response.json();

    document.getElementById(
        "totalDoodles"
    ).innerText =
        data.total;

    document.getElementById(
        "uniqueObjects"
    ).innerText =
        data.unique;

    document.getElementById(
        "topObject"
    ).innerText =
        data.top.toUpperCase();

        document.getElementById(
    "flashcardCount"
).innerText =
    data.flashcards;

document.getElementById(
    "chatCount"
).innerText =
    data.chats;

document.getElementById(
    "learningStreak"
).innerText =
    data.streak;

document.getElementById(
    "topTopic"
).innerText =
    data.topic.toUpperCase();

    const list =
        document.getElementById(
            "recentList"
        );

    list.innerHTML = "";

    data.recent.forEach(item => {

        const li =
            document.createElement("li");

        li.innerText = item;

        list.appendChild(li);
    });
}

async function loadChart(){

    const response =
        await fetch(
            "http://127.0.0.1:5000/chart_data"
        );

    const data =
        await response.json();

    new Chart(

        document.getElementById(
            "doodleChart"
        ),

        {

            type:"bar",

            data:{

                labels:
                data.labels,

                datasets:[{

                    label:
                    "Doodles Drawn",

                    data:
                    data.counts
                }]
            }
        }
    );
}

function goBack(){

    window.location.href =
        "index.html";
}

loadDashboard();
loadChart();
