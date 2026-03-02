let lastSpotifyState = null;
let suppressYouTubeReaction = false;

async function checkSpotifyState() {
    try {
        const res = await fetch("http://127.0.0.1:5000/state");
        const data = await res.json();

        if (data.is_playing !== lastSpotifyState) {
            lastSpotifyState = data.is_playing;

            if (data.is_playing === true && !suppressYouTubeReaction) {
                chrome.tabs.query({}, (tabs) => {
                tabs.forEach(tab => {
            if (tab.url && tab.url.includes("youtube.com")) {
                chrome.tabs.sendMessage(tab.id, "pauseYouTube");
        }
    });
});
            }

            suppressYouTubeReaction = false;
        }
    } catch (e) {}
}

setInterval(checkSpotifyState, 3000);

chrome.runtime.onMessage.addListener((message) => {

    if (message === "pauseSpotify") {
        suppressYouTubeReaction = true;
        fetch("http://127.0.0.1:5000/pause");
    }

    if (message === "playSpotify") {
        fetch("http://127.0.0.1:5000/play");
    }

});