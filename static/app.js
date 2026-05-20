const chatForm = document.getElementById("chat-form");
const userMessageInput = document.getElementById("user_message");
const voiceBtn = document.getElementById("voice-btn");
const voiceStatus = document.getElementById("voice-status");
const aiResponseBox = document.getElementById("ai-response");
const speakBtn = document.getElementById("speak-btn");
const activityLogBox = document.getElementById("activity-log");
const filesUsedBox = document.getElementById("files-used");

const chatAgent = document.getElementById("chat-agent");
const chatAgentStatus = chatAgent.querySelector("small");

const fileAgent = document.getElementById("file-agent");
const fileAgentStatus = fileAgent.querySelector("small");

const memoryAgent = document.getElementById("memory-agent");
const memoryAgentStatus = memoryAgent.querySelector("small");

const toolAgent = document.getElementById("tool-agent");
const toolAgentStatus = toolAgent.querySelector("small");

const stageChat = document.querySelector(".stage-chat");
const stageFile = document.querySelector(".stage-file");
const stageMemory = document.querySelector(".stage-memory");
const stageTool = document.querySelector(".stage-tool");

function turnAgentOn(agentCard, agentStatus, statusText) {
    agentCard.classList.add("thinking");
    agentStatus.textContent = statusText;

    if (agentCard === chatAgent) {
        stageChat.classList.add("active-stage-agent");
    }

    if (agentCard === fileAgent) {
        stageFile.classList.add("active-stage-agent");
    }

    if (agentCard === memoryAgent) {
        stageMemory.classList.add("active-stage-agent");
    }

    if (agentCard === toolAgent) {
        stageTool.classList.add("active-stage-agent");
    }
}

function turnAgentOff(agentCard, agentStatus) {
    agentCard.classList.remove("thinking");
    agentStatus.textContent = "idle";

    stageChat.classList.remove("active-stage-agent");
    stageFile.classList.remove("active-stage-agent");
    stageMemory.classList.remove("active-stage-agent");
    stageTool.classList.remove("active-stage-agent");
}

function reactToEvent(eventText) {
    if (eventText.startsWith("tool_agent")) {
        turnAgentOn(toolAgent, toolAgentStatus, "used");
    }

    if (eventText.startsWith("file_agent")) {
        turnAgentOn(fileAgent, fileAgentStatus, "used");
    }

    if (eventText.startsWith("chat_agent")) {
        turnAgentOn(chatAgent, chatAgentStatus, "used");
    }

    if (eventText.startsWith("memory_agent")) {
        turnAgentOn(memoryAgent, memoryAgentStatus, "used");
    }
}

chatForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const userMessage = userMessageInput.value;

    aiResponseBox.textContent = "Thinking...";

    turnAgentOn(chatAgent, chatAgentStatus, "thinking");

    activityLogBox.innerHTML =
        "<div>• User submitted message</div>" +
        "<div>• Chat Agent thinking</div>";

    const response = await fetch("/stream-message", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            message: userMessage
        })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
        const { value, done } = await reader.read();

        if (done) {
            break;
        }

        const chunk = decoder.decode(value);

        const lines = chunk.split("\n");

        lines.forEach(function (line) {
            if (line.startsWith("data: ")) {
                const jsonText = line.replace("data: ", "");
                const eventData = JSON.parse(jsonText);

                console.log("EVENT:", eventData);

                if (eventData.type === "response") {
                    console.log("SETTING RESPONSE:", eventData.response);
                    aiResponseBox.innerText = eventData.response;

                    filesUsedBox.innerHTML = "";

                    eventData.files_used.forEach(function (fileName) {
                        filesUsedBox.innerHTML += `<div>- ${fileName}</div>`;
                    });
                }

                if (eventData.type === "done") {
                    setTimeout(() => {
                        turnAgentOff(chatAgent, chatAgentStatus);
                        turnAgentOff(toolAgent, toolAgentStatus);
                        turnAgentOff(fileAgent, fileAgentStatus);
                        turnAgentOff(memoryAgent, memoryAgentStatus);
                    }, 1000);
                }

                if (eventData.type === "agent") {

                    if (eventData.agent === "tool") {
                        turnAgentOn(toolAgent, toolAgentStatus, eventData.status);
                    }

                    if (eventData.agent === "file") {
                        turnAgentOn(fileAgent, fileAgentStatus, eventData.status);
                    }

                    if (eventData.agent === "memory") {
                        turnAgentOn(memoryAgent, memoryAgentStatus, eventData.status);
                    }

                    if (eventData.agent === "chat") {
                        turnAgentOn(chatAgent, chatAgentStatus, eventData.status);
                    }
                }
            }
        });
    }

    turnAgentOff(chatAgent, chatAgentStatus);

});

const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {

    const recognition = new SpeechRecognition();

    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;

    voiceBtn.addEventListener("click", function () {

        voiceBtn.textContent = "Listening...";

        voiceStatus.textContent = "Listening for speech...";

        recognition.start();

    });

    recognition.addEventListener("result", function (event) {

        const transcript = event.results[0][0].transcript;

        userMessageInput.value = transcript;

        if (transcript.trim() === "") {
            voiceBtn.textContent = "🎙 Talk";
            return;
        }

        voiceBtn.textContent = "Sending...";

        voiceStatus.textContent = `Captured: "${transcript}" — press Send`;

    });

    recognition.addEventListener("end", function () {

        setTimeout(function () {
            voiceBtn.textContent = "🎙 Talk";
            voiceStatus.textContent = "";
        }, 1200);

    });

    recognition.addEventListener("error", function (event) {
        console.log("Speech error:", event.error);
        voiceBtn.textContent = "Mic error";
    });

} else {

    alert("Speech Recognition is not supported in this browser.");

}

let availableVoices = [];

function loadVoices() {
    availableVoices = speechSynthesis.getVoices();
    console.log("Loaded voices:", availableVoices);
}

loadVoices();

speechSynthesis.onvoiceschanged = loadVoices;

speakBtn.addEventListener("click", function () {

    console.log("Speak button clicked");

    const text = aiResponseBox.innerText;

    if (!text.trim()) {
        console.log("No text to speak");
        return;
    }

    if (!window.speechSynthesis) {
        console.log("Speech synthesis not supported");
        alert("Speech synthesis is not supported in this browser.");
        return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    const ziraVoice = availableVoices.find(voice =>
        voice.name.includes("Zira")
    );

    if (ziraVoice) {
        utterance.voice = ziraVoice;
    }

    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.volume = 1;

    speechSynthesis.cancel();
    console.log("Available voices:", availableVoices);
    availableVoices.forEach((voice, index) => {
        console.log(index, voice.name);
    });
    speechSynthesis.speak(utterance);

});