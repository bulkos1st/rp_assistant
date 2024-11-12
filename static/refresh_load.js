async function refreshData() {
    // Show the loading bar container and reset its width
    const loadingBarContainer = document.getElementById("loadingBarContainer");
    const loadingBar = document.getElementById("loadingBar");
    loadingBarContainer.style.display = "block";
    loadingBar.style.width = "0%";

    // Increase the loading bar width gradually
    let progress = 0;
    const interval = setInterval(() => {
        progress += 10;
        loadingBar.style.width = `${progress}%`;
        if (progress >= 90) clearInterval(interval); // Stop at 90% until request completes
    }, 300);

    try {
        // Perform the request to the /refresh endpoint
        const response = await fetch('/refresh_devices', {
            method: 'POST'
        });

        // Ensure the response was successful
        if (response.ok) {
            loadingBar.style.width = "100%"; // Complete the loading bar
            clearInterval(interval);
            setTimeout(() => {
                // Wait briefly, then refresh the page
                window.location.reload();
            }, 500);
        } else {
            throw new Error('Failed to refresh');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error refreshing data. Please try again.');
        loadingBarContainer.style.display = "none"; // Hide the loading bar on error
    }
}