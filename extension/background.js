chrome.runtime.onMessage.addListener((message) => {

    if (message === "pauseSpotify") {
        fetch("http://127.0.0.1:5000/pause");
    }

    if (message === "playSpotify") {
        fetch("http://127.0.0.1:5000/play");
    }

});