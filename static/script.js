async function searchPapers() {
    let query = document.getElementById("searchQuery").value.trim();
    let numResults = document.getElementById("numResults").value;

    if (!query) {
        alert("Please enter a keyword or title.");
        return;
    }

    let resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "<p>Loading...</p>";

    try {
        let response = await fetch(`http://127.0.0.1:5000/search?query=${query}&max_results=${numResults}`);
        let data = await response.json();

        resultsDiv.innerHTML = "";
        if (!data.data.length) {
            resultsDiv.innerHTML = "<p>No results found.</p>";
            return;
        }

        data.data.forEach(paper => {
            let paperDiv = document.createElement("div");
            paperDiv.classList.add("paper");
            paperDiv.innerHTML = `
                <h3>${paper.title}</h3>
                <p><b>Authors:</b> ${paper.authors.join(", ")}</p>
                <p><b>Year:</b> ${paper.year}</p>
                <a href="${paper.url}" target="_blank">Read More</a>
            `;
            resultsDiv.appendChild(paperDiv);
        });
    } catch (error) {
        resultsDiv.innerHTML = "<p>Error fetching data.</p>";
    }
}
