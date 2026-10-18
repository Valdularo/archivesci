(() => {
  const data = window.ARCHIVE_CATALOG;
  const status = document.querySelector("#result-status");
  const resultsList = document.querySelector("#results-list");
  const searchInput = document.querySelector("#search-input");
  const collectionFilter = document.querySelector("#collection-filter");
  const clearButton = document.querySelector("#clear-search");
  const moreButton = document.querySelector("#show-more");
  const collectionGrid = document.querySelector("#collection-grid");
  const pageSize = 40;
  let visibleCount = pageSize;

  if (!data || !status || !resultsList || !searchInput || !collectionFilter || !clearButton || !moreButton || !collectionGrid) {
    return;
  }

  const collections = new Map(data.collections.map((collection) => [collection.id, collection]));
  const normalized = (value) => value.toLocaleLowerCase();

  data.collections.forEach((collection) => {
    const option = document.createElement("option");
    option.value = collection.id;
    option.textContent = collection.title;
    collectionFilter.append(option);

    const card = document.createElement("a");
    card.className = "collection-card";
    card.href = collection.path;
    card.innerHTML = `<div><h3></h3></div><span><span></span><span class="arrow" aria-hidden="true">Open collection →</span></span>`;
    card.querySelector("h3").textContent = collection.title;
    card.querySelector(".collection-card span span").textContent = `${collection.count} transcript${collection.count === 1 ? "" : "s"}`;
    collectionGrid.append(card);
  });

  document.querySelector("#log-count").textContent = data.records.length.toLocaleString();
  document.querySelector("#collection-count").textContent = data.collections.length.toLocaleString();

  function render() {
    const query = normalized(searchInput.value.trim());
    const selectedCollection = collectionFilter.value;
    const matching = data.records.filter((record) => {
      if (selectedCollection && record.collectionId !== selectedCollection) return false;
      if (!query) return true;
      return normalized(`${record.title} ${record.summary} ${record.collection}`).includes(query);
    });

    const visible = matching.slice(0, visibleCount);
    resultsList.replaceChildren();
    if (visible.length === 0) {
      const empty = document.createElement("li");
      empty.className = "empty-state";
      empty.textContent = "No transcripts match that search. Try a different keyword or collection.";
      resultsList.append(empty);
    } else {
      visible.forEach((record) => {
        const item = document.createElement("li");
        const card = document.createElement(record.available ? "a" : "div");
        card.className = "result-card";
        if (record.available) card.href = record.path;
        card.innerHTML = `<div><h3></h3><p></p></div><span class="result-meta"><span></span><span aria-hidden="true">→</span></span>`;
        card.querySelector("h3").textContent = record.title;
        card.querySelector("p").textContent = record.summary || "No description was provided for this transcript.";
        card.querySelector(".result-meta span").textContent = record.collection;
        if (!record.available) {
          const unavailable = document.createElement("span");
          unavailable.className = "unavailable";
          unavailable.textContent = "Not captured";
          card.querySelector(".result-meta").append(unavailable);
          card.querySelector(".result-meta span[aria-hidden]").remove();
        }
        item.append(card);
        resultsList.append(item);
      });
    }

    const shown = Math.min(visibleCount, matching.length);
    status.textContent = query || selectedCollection
      ? `${matching.length.toLocaleString()} matching transcript${matching.length === 1 ? "" : "s"}${matching.length > shown ? ` · showing ${shown}` : ""}`
      : `${matching.length.toLocaleString()} transcripts in the archive`;
    moreButton.hidden = matching.length <= shown;
    clearButton.hidden = !query && !selectedCollection;
  }

  searchInput.addEventListener("input", () => { visibleCount = pageSize; render(); });
  collectionFilter.addEventListener("change", () => { visibleCount = pageSize; render(); });
  document.querySelector("#search-form").addEventListener("submit", (event) => {
    event.preventDefault();
    render();
  });
  clearButton.addEventListener("click", () => {
    searchInput.value = "";
    collectionFilter.value = "";
    visibleCount = pageSize;
    render();
    searchInput.focus();
  });
  moreButton.addEventListener("click", () => {
    visibleCount += pageSize;
    render();
  });
  render();
})();
