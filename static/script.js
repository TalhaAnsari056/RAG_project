// console.log("Javascript Connected");
// const button = document.getElementById("send-btn");

// const input = document.getElementById("question");

// const chatBox = document.getElementById("chat-box");


// button.addEventListener("click", async () => {

//     // const question = input.value;
//     console.log("send button clicked")
//  const question = input.value.trim();

//     if (question === "") return;


//     const response = await fetch("/chat", {

//         method: "POST",

//         headers: {

//             "Content-Type": "application/json"

//         },

//         body: JSON.stringify({

//             question: question

//         })

//     });
//   const data = await response.json();

//     let html = `

//         <p><b>You:</b> ${question}</p>

//         <p><b>Bot:</b> ${data.answer}</p>

//     `;

//     if (data.pages.length > 0) {

//         html += `

//         <p><b>Source Pages:</b> ${data.pages.join(", ")}</p>

//         <p><b>Similarity Scores:</b> ${data.scores.join(", ")}</p>

//         `;

//     }

//     html += "<hr>";

//     chatBox.innerHTML += html;
// //     const data = await response.json();
// //     const pages =
// //     data.pages.length > 0
// //         ? data.pages.join(", ")
// //         : "None";

// // const scores =
// //     data.scores.length > 0
// //         ? data.scores.join(", ")
// //         : "None";


// // chatBox.innerHTML += `

// // <p><b>You:</b> ${question}</p>

// // <p><b>Bot:</b> ${data.answer}</p>

// // <p><b>Source Pages:</b> ${pages}</p>

// // <p><b>Similarity Scores:</b> ${scores}</p>

// // <hr>

// // `;

// chatBox.scrollTop = chatBox.scrollHeight;
// //     chatBox.innerHTML += `

// // <p><b>You:</b> ${question}</p>

// // <p><b>Bot:</b> ${data.answer}</p>

// // <p><b>Source Pages:</b> ${data.pages.join(", ")}</p>

// // <hr>

// // `;

// //     chatBox.scrollTop = chatBox.scrollHeight;
//     // chatBox.innerHTML += `

//     // <p><b>You:</b> ${question}</p>

//     // <p><b>Bot:</b> ${data.answer}</p>

//     // <hr>

//     // `;

//     input.value = "";

// });
const chatBox = document.getElementById("chat-box");
const input = document.getElementById("question");
const sendBtn = document.getElementById("send-btn");

// -----------------------------
// Pipeline Steps
// -----------------------------

const pipeline = [
    "step-question",
    "step-embedding",
    "step-retriever",
    "step-prompt",
    "step-llm",
    "step-answer"
];

// -----------------------------
// Activate Pipeline
// -----------------------------

async function animatePipeline() {

    // Reset

    pipeline.forEach(id => {
        document.getElementById(id).classList.remove("active");
    });

    for (let id of pipeline) {

        document.getElementById(id).classList.add("active");

        await new Promise(resolve => setTimeout(resolve, 350));

    }

}

// -----------------------------
// Typing Animation
// -----------------------------

function addTypingBubble() {

    const div = document.createElement("div");

    div.className = "bot-message";

    div.id = "typing";

    div.innerHTML = `
        <div class="typing">
            Thinking
            <span>.</span>
            <span>.</span>
            <span>.</span>
        </div>
    `;

    chatBox.appendChild(div);

    chatBox.scrollTop = chatBox.scrollHeight;

}

function removeTypingBubble() {

    const typing = document.getElementById("typing");

    if (typing) {

        typing.remove();

    }

}

// -----------------------------
// Send Message
// -----------------------------

async function sendMessage() {
     console.log("send button clicked")

    const question = input.value.trim();

    if (question === "") return;

    // User Bubble

    const user = document.createElement("div");

    user.className = "user-message";

    user.innerHTML = question;

    chatBox.appendChild(user);

    chatBox.scrollTop = chatBox.scrollHeight;

    input.value = "";

    addTypingBubble();

    animatePipeline();

    const response = await fetch("/chat", {

        method: "POST",

        headers: {

            "Content-Type": "application/json"

        },

        body: JSON.stringify({

            question: question

        })

    });

    const data = await response.json();
    console.log(data.runtime);
    removeTypingBubble();

    const bot = document.createElement("div");

    bot.className = "bot-message";

    let html = `<b>Answer</b><br><br>${data.answer}`;

    if (data.pages.length > 0) {

        html += `

        <hr>

        <b>Source Pages</b><br>

        ${data.pages.join(", ")}

        <br><br>

        <b>Similarity</b><br>

        ${data.scores.join("<br>")}

        `;

    }

    bot.innerHTML = html;

    chatBox.appendChild(bot);

    chatBox.scrollTop = chatBox.scrollHeight;

}

// -----------------------------
// Button
// -----------------------------

sendBtn.addEventListener("click", sendMessage);

// -----------------------------
// Enter Key
// -----------------------------

input.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {

        sendMessage();

    }

});