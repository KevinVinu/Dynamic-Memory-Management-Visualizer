let physicalMemory = [];
let pageSize = 4;
let totalFrames = 8;
let pageFaults = 0;
let pageReferences = [];
let currentStep = 0;
let history = [];

const memoryDisplay = document.getElementById("memoryDisplay");
const status = document.getElementById("status");
const historyBody = document.getElementById("historyBody");

function initializeMemory() {
    pageSize = parseInt(document.getElementById("pageSize").value);
    totalFrames = parseInt(document.getElementById("numFrames").value);
    physicalMemory = Array(totalFrames).fill(-1);
    pageFaults = 0;
    currentStep = 0;
    history = [];
    pageReferences = [];
    historyBody.innerHTML = "";
    drawMemory();
    status.textContent = "Status: Memory initialized";
}

function drawMemory() {
    memoryDisplay.innerHTML = "";
    physicalMemory.forEach((page, index) => {
        const frame = document.createElement("div");
        frame.className = "frame";
        frame.textContent = page === -1 ? "Empty" : page;
        frame.classList.add(page === -1 ? "empty" : "filled");
        memoryDisplay.appendChild(frame);
    });
}

async function runFIFO() {
    const refString = document.getElementById("pageRefs").value;
    pageReferences = refString.split(",").map(x => parseInt(x.trim())).filter(x => !isNaN(x));
    if (pageReferences.length === 0) {
        alert("Please enter valid page references (comma-separated numbers)");
        return;
    }

    pageFaults = 0;
    let queue = [];
    history = [];

    for (let page of pageReferences) {
        let action = "Hit";
        if (!physicalMemory.includes(page)) {
            pageFaults++;
            action = "Page Fault";
            if (queue.length < totalFrames) {
                physicalMemory[queue.length] = page;
                queue.push(page);
            } else {
                const oldPage = queue.shift();
                const frameIdx = physicalMemory.indexOf(oldPage);
                physicalMemory[frameIdx] = page;
                queue.push(page);
            }
            drawMemory();
            status.textContent = `Status: Page Faults: ${pageFaults}`;
            await new Promise(resolve => setTimeout(resolve, 500));
        }
        history.push({ page, action, faults: pageFaults });
        updateHistory();
    }
    alert(`Simulation complete!\nTotal Page Faults: ${pageFaults}`);
}

function stepThrough() {
    const refString = document.getElementById("pageRefs").value;
    pageReferences = refString.split(",").map(x => parseInt(x.trim())).filter(x => !isNaN(x));
    if (pageReferences.length === 0) {
        alert("Please enter valid page references (comma-separated numbers)");
        return;
    }

    if (currentStep >= pageReferences.length) {
        alert(`Simulation complete!\nTotal Page Faults: ${pageFaults}`);
        return;
    }

    let queue = physicalMemory.filter(page => page !== -1);
    let page = pageReferences[currentStep];
    let action = "Hit";

    if (!physicalMemory.includes(page)) {
        pageFaults++;
        action = "Page Fault";
        if (queue.length < totalFrames) {
            physicalMemory[queue.length] = page;
            queue.push(page);
        } else {
            const oldPage = queue.shift();
            const frameIdx = physicalMemory.indexOf(oldPage);
            physicalMemory[frameIdx] = page;
            queue.push(page);
        }
        drawMemory();
        status.textContent = `Status: Page Faults: ${pageFaults}`;
    }

    history.push({ page, action, faults: pageFaults });
    updateHistory();
    currentStep++;
}

function updateHistory() {
    historyBody.innerHTML = "";
    history.forEach(entry => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${entry.page}</td>
            <td>${entry.action}</td>
            <td>${entry.faults}</td>
        `;
        historyBody.appendChild(row);
    });
}

function clearMemory() {
    physicalMemory = Array(totalFrames).fill(-1);
    document.getElementById("pageRefs").value = "";
    pageFaults = 0;
    currentStep = 0;
    history = [];
    historyBody.innerHTML = "";
    drawMemory();
    status.textContent = "Status: Memory cleared";
}

function toggleTheme() {
    document.body.classList.toggle("dark");
    const icon = document.getElementById("themeToggle").querySelector("i");
    icon.classList.toggle("fa-moon");
    icon.classList.toggle("fa-sun");
}

// Initial setup
initializeMemory();