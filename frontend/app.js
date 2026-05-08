const API_BASE_URL = "https://mu-5cd4137b7ef64bddaa570a12c9c2ac25.ecs.us-east-1.on.aws";

function showMessage(id, text, isError = true) {
    const msg = document.getElementById(id);
    if (msg) {
        msg.innerText = text;
        msg.style.color = isError ? "#dc2626" : "#16a34a";
    }
}

async function loginUser() {
    const email = document.getElementById("loginEmail").value.trim();
    const password = document.getElementById("loginPassword").value.trim();

    const response = await fetch(`${API_BASE_URL}/login`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({email, password})
    });

    const data = await response.json();

    if (response.ok) {
        localStorage.setItem("email", data.email);
        localStorage.setItem("user_name", data.user_name);
        window.location.href = "main.html";
    } else {
        showMessage("loginMessage", data.message || "email or password is invalid");
    }
}

async function registerUser() {
    const user_name = document.getElementById("registerUsername").value.trim();
    const email = document.getElementById("registerEmail").value.trim();
    const password = document.getElementById("registerPassword").value.trim();

    if (!user_name || !email || !password) {
        showMessage("registerMessage", "All fields are required");
        return;
    }

    if (!email.includes("@")) {
        showMessage("registerMessage", "Please enter a valid email address");
        return;
    }

    const response = await fetch(`${API_BASE_URL}/register`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({email, user_name, password})
    });

    const data = await response.json();

    if (response.ok) {
        showMessage("registerMessage", "Registration successful. Redirecting to login...", false);
        setTimeout(() => {
            window.location.href = "index.html";
        }, 1200);
    } else {
        showMessage("registerMessage", data.message || "Registration failed");
    }
}

function loadDashboard() {
    const email = localStorage.getItem("email");
    const userName = localStorage.getItem("user_name");

    if (!email) {
        window.location.href = "index.html";
        return;
    }

    document.getElementById("welcomeUser").innerText = `Welcome, ${userName}`;
    loadSubscriptions();
}

async function queryMusic() {
    const title = document.getElementById("searchTitle").value.trim();
    const year = document.getElementById("searchYear").value.trim();
    const artist = document.getElementById("searchArtist").value.trim();
    const album = document.getElementById("searchAlbum").value.trim();

    const resultsDiv = document.getElementById("musicResults");
    const queryMessage = document.getElementById("queryMessage");

    resultsDiv.innerHTML = "";

    if (!title && !year && !artist && !album) {
        showMessage("queryMessage", "At least one field must be completed");
        return;
    }

    showMessage("queryMessage", "Searching music...", false);
    queryMessage.classList.add("loading-text");

    const params = new URLSearchParams();

    if (title) params.append("title", title);
    if (year) params.append("year", year);
    if (artist) params.append("artist", artist);
    if (album) params.append("album", album);

    try {
        const response = await fetch(`${API_BASE_URL}/music?${params.toString()}`);
        const data = await response.json();

        queryMessage.classList.remove("loading-text");

        if (!response.ok) {
            showMessage("queryMessage", data.message || "No result is retrieved. Please query again");
            return;
        }

        showMessage("queryMessage", `${data.length} result(s) found`, false);

        data.forEach(song => {
            resultsDiv.innerHTML += createMusicCard(song, "subscribe");
        });

    } catch (error) {
        queryMessage.classList.remove("loading-text");
        showMessage("queryMessage", "Unable to connect to backend. Please try again.");
    }
}

async function loadSubscriptions() {
    const email = localStorage.getItem("email");

    const response = await fetch(`${API_BASE_URL}/subscriptions?email=${encodeURIComponent(email)}`);
    const data = await response.json();

    const subDiv = document.getElementById("subscriptionsList");
    subDiv.innerHTML = "";

    if (data.length === 0) {
        subDiv.innerHTML = `<p class="empty-text">No subscriptions yet. Search and subscribe to your favourite songs.</p>`;
        return;
    }

    data.forEach(song => {
        subDiv.innerHTML += createMusicCard(song, "remove");
    });
}

let songStore = {};

function createMusicCard(song, actionType) {
    const imageUrl = `https://music-app-images-group18.s3.amazonaws.com/${song.image_url}`;
    const safeId = btoa(unescape(encodeURIComponent(song.song_id)));

    songStore[safeId] = song;

    let buttonHtml = "";

    if (actionType === "subscribe") {
        buttonHtml = `<button onclick="subscribeSongById('${safeId}')">Subscribe</button>`;
    } else {
        buttonHtml = `<button class="remove-btn" onclick="removeSubscription('${song.song_id.replace(/'/g, "\\'")}')">Remove</button>`;
    }

    return `
        <div class="music-card">
            <img src="${imageUrl}" alt="${song.artist}">
            <h4>${song.title}</h4>
            <p><strong>Artist:</strong> ${song.artist}</p>
            <p><strong>Album:</strong> ${song.album}</p>
            <p><strong>Year:</strong> ${song.year}</p>
            ${buttonHtml}
        </div>
    `;
}

function subscribeSongById(songId) {
    const song = songStore[songId];
    subscribeSong(song);
}

async function subscribeSong(song) {
    const email = localStorage.getItem("email");

    const payload = {
        email: email,
        song_id: song.song_id,
        title: song.title,
        artist: song.artist,
        album: song.album,
        year: song.year,
        image_url: song.image_url
    };

    await fetch(`${API_BASE_URL}/subscriptions`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
    });

    loadSubscriptions();
    showMessage("queryMessage", "Song subscribed successfully", false);
}

async function removeSubscription(songId) {
    const email = localStorage.getItem("email");

    await fetch(`${API_BASE_URL}/subscriptions`, {
        method: "DELETE",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            email: email,
            song_id: songId
        })
    });

    loadSubscriptions();
}

function scrollToSubscriptions() {
    const section = document.getElementById("subscriptionSection");

    if (section) {
        section.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    }
}

function logoutUser() {
    localStorage.clear();
    window.location.href = "index.html";
}

