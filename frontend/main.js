let currentX = 0;
let currentY = -1;
let data;
const keyboard = document.getElementById("keyboard");
const board = document.getElementById("board");
for (let y = 0; y < 6; y++) {
    const row = document.createElement("div");
    row.classList.add("row");
    board.appendChild(row);
    for (let x = 0; x < 5; x++) {
        const box = document.createElement("div");
        box.setAttribute("style", `transition-delay: ${25 * x}ms;`)
        row.appendChild(box);
    }
}
const leaderboard = document.getElementById("leaderboard");
const leaderboardHead = createAndFillElement("thead", leaderboard);
createAndFillElement("th", leaderboardHead, "Место");
createAndFillElement("th", leaderboardHead, "Игрок");
createAndFillElement("th", leaderboardHead, "Побед");
createAndFillElement("th", leaderboardHead, "Попытки/победы");
createAndFillElement("th", leaderboardHead, "Время/попытки");
const leaderboardBody = createAndFillElement("tbody", leaderboard);
let endpoint = "/api/";
if (location.hostname === "localhost") {
    endpoint = "http://localhost:5000/";
}
update();
setInterval(update, 60 * 1000);

const Status = {
    WRONG: 0,
    WRONG_SPOT: 1,
    CORRECT: 2,
};

async function request(url, params) {
    return fetch(url + "?" + new URLSearchParams(params).toString(), { credentials: 'include' });
}

function createAndFillElement(element, parent, value) {
    const newElement = document.createElement(element);
    if (value !== undefined) newElement.innerHTML = value;
    parent.appendChild(newElement);
    return newElement;
}

document.addEventListener("keyup", async (e) => {
    if (data === undefined || !data.available) {
        return;
    }

    let key = e.key;
    if (key === "Unidentified") {
        key = keyboard.value.slice(-1);
    }
    keyboard.value = "";
    key = key.toLowerCase();

    if (key === "enter" && currentX === 5) {
        let word = "";
        for (let x = 0; x < 5; x++) {
            word += board.children[currentY].children[x].innerHTML;
        }
        let check = await request(endpoint + "check", { "word": word })
        if (!check.ok) return;
        check = await check.json();
        for (let x = 0; x < 5; x++) {
            board.children[currentY].children[x].classList.add(Object.keys(Status)[check[x]]);
        }
        ++currentY;
        currentX = 0;
        if (currentY === 6 || check.filter(x => x === Status.CORRECT).length === check.length) {
            update();
        }
        if (check.length == 6) {
            alert(`Слово было: ${check[5]}!`);
        }
    } else if (key === "backspace" && currentX > 0) {
        board.children[currentY].children[--currentX].innerHTML = "";
    } else if (key.match(/[а-я]/) && currentX < 5) {
        board.children[currentY].children[currentX++].innerHTML = key;
    }
});

async function update() {
    const get = await request(endpoint + "get");
    board.className = "";
    document.getElementById("gid").hidden = get.ok;
    if (get.ok) {
        data = await get.json();
    }

    function createLeaderboardRow(user, place) {
        let name = user.name;
        if (data !== undefined && user._id === data._id) {
            imcool = true;
            name += " (ты)";
        }

        const row = createAndFillElement("tr", leaderboardBody);
        createAndFillElement("td", row, place);
        createAndFillElement("td", row, name);
        createAndFillElement("td", row, user.totalWins);
        createAndFillElement("td", row, (user.totalAttempts / user.totalWins).toFixed(2));
        createAndFillElement("td", row, (user.totalTime / user.totalAttempts).toFixed(2));
    }
    let imcool = false;
    let place = 0;
    let leaderboard_ = await request(endpoint + "leaderboard");
    leaderboard_ = await leaderboard_.json();
    leaderboardBody.innerHTML = "";
    leaderboard_.forEach(user => createLeaderboardRow(user, ++place));
    if (!imcool) {
        createLeaderboardRow(data, "-");
    }

    if (data !== undefined && data.attempts.length === currentY) return;
    currentY = data.attempts.length;


    for (let y = 0; y < board.children.length; y++) {
        for (let x = 0; x < board.children[y].children.length; x++) {
            const box = board.children[y].children[x];
            box.innerHTML = "";
            box.className = "";
            box.classList.add("box", "font");
            try {
                box.innerHTML = data.attempts[y][0][x];
                box.classList.add(Object.keys(Status)[data.attempts[y][1][x]]);
            } catch { }
        }
    }
}