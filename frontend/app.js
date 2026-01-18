// frontend/app.js
async function runSearch() {
  const queryInput = document.getElementById("query");
  const query = queryInput.value.trim();

  if (!query) {
    alert("Пожалуйста, введите описание юридической ситуации");
    queryInput.focus();
    return;
  }

  const searchBtn = document.querySelector(".search-btn");
  searchBtn.disabled = true;
  searchBtn.textContent = "Анализирую...";

  // Показываем индикатор загрузки
  document.getElementById("results").innerHTML = `
        <div class="loading">
            <div class="loading-spinner"></div>
            <p>Ищу судебную практику и материалы...</p>
        </div>
    `;

  document.getElementById("analysis").innerHTML = `
        <div class="loading">
            <div class="loading-spinner"></div>
            <p>Готовлю подробный юридический анализ...</p>
        </div>
    `;

  try {
    // Поиск материалов
    const searchResp = await fetch("http://localhost:8000/api/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, limit: 12 }),
    });

    if (!searchResp.ok) {
      throw new Error(`Ошибка поиска: ${searchResp.statusText}`);
    }

    const searchData = await searchResp.json();
    renderResults(searchData.results);

    if (searchData.results.length === 0) {
      document.getElementById("analysis").innerHTML = `
                <div class="no-results">
                    <h3>Ничего не найдено</h3>
                    <p>По вашему запросу не найдено судебных решений или юридических материалов.
                    Попробуйте изменить формулировку запроса или добавить больше деталей.</p>
                </div>
            `;
      return;
    }

    // Подготовка документов для анализа
    const docs = searchData.results.map((r) => ({
      title: r.title,
      text: `${r.snippet} Источник: ${r.source}`,
    }));

    // Анализ материалов
    const analyzeResp = await fetch("http://localhost:8000/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, documents: docs }),
    });

    if (!analyzeResp.ok) {
      // Получаем детали ошибки от сервера
      const errorData = await analyzeResp.json().catch(() => null);
      const errorMessage =
        errorData?.detail ||
        `Ошибка сервера: ${analyzeResp.status} ${analyzeResp.statusText}`;
      throw new Error(errorMessage);
    }

    const analyzeData = await analyzeResp.json();
    document.getElementById("analysis").innerHTML = marked.parse(
      analyzeData.result,
    );
  } catch (error) {
    console.error("Ошибка:", error);
    document.getElementById("analysis").innerHTML = `
            <div class="error">
                <h3>Ошибка при анализе</h3>
                <p>${error.message.replace(/\n/g, "<br>")}</p>
                <p>Попробуйте повторить запрос позже или изменить формулировку.</p>
                <button onclick="runSearch()" class="retry-btn">Повторить попытку</button>
            </div>
        `;
  } finally {
    searchBtn.disabled = false;
    searchBtn.textContent = "Анализировать";
  }
}

function renderResults(results) {
  const container = document.getElementById("results");

  if (results.length === 0) {
    container.innerHTML = `
            <div class="no-results">
                <h3>Ничего не найдено</h3>
                <p>По вашему запросу не найдено судебных решений или юридических материалов.</p>
            </div>
        `;
    return;
  }

  let html = "";
  results.forEach((result, index) => {
    html += `
            <div class="result-item">
                <div class="result-title">
                    <a href="${result.url}" target="_blank" rel="noopener noreferrer">
                        ${result.title || "Без названия"}
                    </a>
                </div>
                <div class="result-snippet">
                    ${result.snippet || "Нет описания"}
                </div>
                <div class="result-source">
                    Источник: ${result.source}
                </div>
            </div>
        `;
  });

  container.innerHTML = html;
}

// Обработка нажатия Enter в поле ввода
document.getElementById("query").addEventListener("keypress", function (event) {
  if (event.key === "Enter") {
    runSearch();
  }
});
