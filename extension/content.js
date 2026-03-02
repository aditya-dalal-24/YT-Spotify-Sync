let currentVideo = null;
let lastState = null;

function attach(video) {

    if (video === currentVideo) return;

    currentVideo = video;
    lastState = null;

    video.addEventListener("play", () => {
        if (lastState !== "playing") {
            lastState = "playing";
            chrome.runtime.sendMessage("pauseSpotify");
        }
    });

    video.addEventListener("pause", () => {
        if (!video.ended && lastState !== "paused") {
            lastState = "paused";
            chrome.runtime.sendMessage("playSpotify");
        }
    });
}

setInterval(() => {
    const video = document.querySelector("video");
    if (video) attach(video);
}, 1000);

chrome.runtime.onMessage.addListener((message) => {
    if (message === "pauseYouTube") {
        const video = document.querySelector("video");
        if (video && !video.paused) {
            video.pause();
        }
    }
});