const chatBox = document.getElementById("chat-box");
const input = document.getElementById("question");
const sendBtn = document.getElementById("send-btn");

// Dashboard Cards
const agentCard = document.getElementById("agent-name");
const confidenceValue = document.getElementById("confidence-value");
const confidenceBar = document.getElementById("confidence-bar");
const similarityCard = document.getElementById("similarity");
const runtimeCard = document.getElementById("runtime");
const chunksPanel = document.getElementById("chunks-panel");


// ------------------------------
// Runtime Pipeline Animation
// ------------------------------

async function animateRuntimePipeline(steps) {

    if (!steps) return;

    document.querySelectorAll(".node").forEach(n => {

        n.classList.remove("active");

    });

    document.querySelectorAll(".line").forEach(l => {

        l.classList.remove("active");

    });

    const mapping = {

        "Question": "node-question",

        "Embedding": "node-embedding",

        "Vector Search": "node-vector",

        "Similarity Check": "node-threshold",

        "Router": "node-router",

        "Greeting Agent": "node-greeting",

        "PDF Agent": "node-rag",

        "Scope Agent": "node-scope",

        "LLM": "node-llm",

        "Final Answer": "node-answer"

    };

    const lines = document.querySelectorAll(".line");

    let lineIndex = 0;

    for (const step of steps) {

        const id = mapping[step];

        if (id) {

            const node = document.getElementById(id);

            node.classList.add("active");
            // await activateNode(node);

            const line = node.previousElementSibling;

            if (line && line.classList.contains("line")) {

                line.classList.add("active");

            }
        }

        if (lines[lineIndex]) {

            lines[lineIndex].classList.add("active");

        }

        lineIndex++;

        await new Promise(r => setTimeout(r, 450));

    }

}



// ------------------------------
// Typing Bubble
// ------------------------------

function addTypingBubble() {

    const div = document.createElement("div");

    div.id = "typing";

    div.className = "bot-message";

    div.innerHTML = "Thinking<span>.</span><span>.</span><span>.</span>";

    chatBox.appendChild(div);

    chatBox.scrollTop = chatBox.scrollHeight;

}

function removeTypingBubble() {

    const t = document.getElementById("typing");

    if (t) t.remove();

}



// ------------------------------
// Dashboard Update
// ------------------------------

function updateDashboard(data) {

    agentCard.innerHTML = data.agent;

    confidenceValue.innerHTML = data.confidence + " %";

    confidenceBar.style.width = data.confidence + "%";
    console.log("Raw API value:", data.best_score);
    console.log("Type of raw value:", typeof data.best_score);

    // 1. Format the score first
    const formatted = (data.best_score !== null && data.best_score !== undefined)
        ? Number(data.best_score).toFixed(3)
        : "-";

    console.log("Formatted string value:", formatted);

    // 2. Assign the formatted value safely
    if (data.scores && data.scores.length > 0) {
        similarityCard.innerHTML = formatted;
        console.log("DOM element value (IF block):", similarityCard.innerHTML);
    } else {
        // This else block was overwriting your hard work with the raw value!
        similarityCard.innerHTML = formatted;
        console.log("DOM element value (ELSE block):", similarityCard.innerHTML);
    }

    runtimeCard.innerHTML = `

<div>Embedding : ${data.runtime.embedding} sec</div>

<div>Retrieval : ${data.runtime.retrieval} sec</div>

<div>LLM : ${data.runtime.llm} sec</div>

<hr>

<div><b>Total : ${data.runtime.total} sec</b></div>

`;


    chunksPanel.innerHTML = "";



    if (data.chunks.length === 0) {

        chunksPanel.innerHTML = "No retrieved chunks.";

        return;

    }



    data.chunks.forEach(chunk => {

        chunksPanel.innerHTML += `

        <div class="chunk">

        <b>Page ${chunk.page}</b>

        <br><br>

        ${chunk.text}

        </div>

        `;

    });

}

function updateNodeRuntime(runtime) {

    document.getElementById("time-question").innerHTML = "-";

    document.getElementById("time-embedding").innerHTML =
        runtime.embedding.toFixed(3) + " s";

    document.getElementById("time-vector").innerHTML =
        runtime.retrieval.toFixed(3) + " s";

    document.getElementById("time-threshold").innerHTML =
        runtime.retrieval.toFixed(3) + " s";

    document.getElementById("time-router").innerHTML = "-";

    document.getElementById("time-greeting").innerHTML = "-";

    document.getElementById("time-scope").innerHTML = "-";

    document.getElementById("time-rag").innerHTML = "-";

    document.getElementById("time-llm").innerHTML =
        runtime.llm.toFixed(3) + " s";

    document.getElementById("time-answer").innerHTML =
        runtime.total.toFixed(3) + " s";

}

// ------------------------------
// Send Message
// ------------------------------

async function sendMessage() {

    const question = input.value.trim();

    if (question === "") return;

    const user = document.createElement("div");

    user.className = "user-message";

    user.innerHTML = question;

    chatBox.appendChild(user);

    chatBox.scrollTop = chatBox.scrollHeight;

    input.value = "";



    addTypingBubble();

    let response;

    try {

        response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question: question
            })

        });

        if (!response.ok) {

            throw new Error(`HTTP ${response.status}`);

        }

    } catch (err) {

        console.error("Request Failed:", err);

        const bubble = document.getElementById("typing");

        if (bubble) {
            bubble.remove();
        }

        // addBotMessage(
        //     "❌ Unable to connect to the AI assistant. Please try again."
        // );
        const bot = document.createElement("div");

        bot.className = "bot-message";

        bot.innerHTML = "❌ Unable to connect to the AI assistant.";

        chatBox.appendChild(bot);

        chatBox.scrollTop = chatBox.scrollHeight;

        return;

    }

    const data = await response.json();

    // const response = await fetch("/chat", {

    //     method: "POST",

    //     headers: {

    //         "Content-Type": "application/json"

    //     },

    //     body: JSON.stringify({

    //         question: question

    //     })

    // });


    removeTypingBubble();



    updateDashboard(data);

    // Update runtime on every node
    updateNodeRuntime(data.runtime);
    // Animate architecture
    animateRuntimePipeline(data.pipeline);



    const bot = document.createElement("div");
    bot.className = "bot-message";

    let html = `
    <b>Agent</b>
    <br>
    ${data.agent}
    <br><br>
    <b>Answer</b>
    <br><br>
    ${data.answer}
    `;

    if (data.pages && data.pages.length > 0) {
        // Map over the pages array. If a page number is null, undefined, or 0, 
        // display a readable tag instead of the word 'null'.
        const cleanPages = data.pages.map(p => {
            return (p !== null && p !== undefined && p !== 0) ? p : "Image/Scanned Page";
        });

        html += `
        <hr>
        <b>Source Pages</b>
        <br>
        ${cleanPages.join(", ")}
        `;
    }

    bot.innerHTML = html;
    chatBox.appendChild(bot);
    chatBox.scrollTop = chatBox.scrollHeight;
}




// ------------------------------

sendBtn.addEventListener("click", sendMessage);

input.addEventListener("keypress", (e) => {

    if (e.key === "Enter") {

        sendMessage();

    }

});