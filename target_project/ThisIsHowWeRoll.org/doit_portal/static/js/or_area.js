document.addEventListener("DOMContentLoaded", () => {
  const openBtn = document.getElementById("openCampaignModal");
  const closeBtn = document.getElementById("closeCampaignModal");
  const modal = document.getElementById("campaignModal");

  if (!openBtn || !closeBtn || !modal) return;

  const campaignForm = modal.querySelector("form");

  openBtn.addEventListener("click", () => {
    modal.classList.add("show");

    if (campaignForm) {
      campaignForm.reset();
    }

    document.querySelector('[name="campaign_id"]').value = "";
  });

  closeBtn.addEventListener("click", () => {
    modal.classList.remove("show");
  });

  modal.addEventListener("click", (event) => {
    if (event.target === modal) {
      modal.classList.remove("show");
    }
  });

  const startDateInput = document.querySelector('input[name="start_date"]');
  const endDateInput = document.querySelector('input[name="end_date"]');

  if (startDateInput && endDateInput) {
    startDateInput.addEventListener("change", () => {
      endDateInput.min = startDateInput.value;

      if (!endDateInput.value || endDateInput.value < startDateInput.value) {
        endDateInput.value = startDateInput.value;
      }
    });
  }

  const editButtons = document.querySelectorAll(".edit-btn");

  editButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      modal.classList.add("show");

      document.querySelector('[name="campaign_id"]').value = btn.dataset.id || "";
      document.querySelector('[name="contract_number"]').value = btn.dataset.contract || "";
      document.querySelector('[name="campaign"]').value = btn.dataset.campaign || "";
      document.querySelector('[name="city"]').value = btn.dataset.city || "";
      document.querySelector('[name="state"]').value = btn.dataset.state || "";
      document.querySelector('[name="start_date"]').value = btn.dataset.start || "";
      document.querySelector('[name="end_date"]').value = btn.dataset.end || "";
      document.querySelector('[name="notes"]').value = btn.dataset.notes || "";

      const days = JSON.parse(btn.dataset.days || "[]");

      document.querySelectorAll('input[name="run_days"]').forEach((cb) => {
        cb.checked = days.includes(cb.value);
      });
    });
  });
});


const filterInputs = document.querySelectorAll(".or-filter-input");
const calendarRows = document.querySelectorAll(".or-calendar-table tbody tr");

filterInputs.forEach((input) => {
  input.addEventListener("input", () => {
    calendarRows.forEach((row) => {
      let rowMatches = true;

      filterInputs.forEach((filter) => {
        const searchText = filter.value.toLowerCase().trim();
        const colIndex = Number(filter.dataset.col);

        if (!searchText) return;

        const cell = row.children[colIndex];

        if (!cell || !cell.textContent.toLowerCase().includes(searchText)) {
          rowMatches = false;
        }
      });

      row.style.display = rowMatches ? "" : "none";
    });
  });
});



const sortableHeaders = document.querySelectorAll(".sortable");

sortableHeaders.forEach((header) => {
  header.addEventListener("click", () => {
    const table = header.closest("table");
    const tbody = table.querySelector("tbody");

    const rows = Array.from(tbody.querySelectorAll("tr"));

    const colIndex = Number(header.dataset.col);

    const ascending = !header.classList.contains("sort-asc");

    sortableHeaders.forEach((h) => {
      h.classList.remove("sort-asc", "sort-desc");
    });

    header.classList.add(ascending ? "sort-asc" : "sort-desc");

    rows.sort((a, b) => {
      const aCell = a.children[colIndex];
      const bCell = b.children[colIndex];

      const aSelect = aCell.querySelector("select");
      const bSelect = bCell.querySelector("select");

      const aText = aSelect
        ? aSelect.value.toLowerCase()
        : aCell.innerText.trim().toLowerCase();

      const bText = bSelect
        ? bSelect.value.toLowerCase()
        : bCell.innerText.trim().toLowerCase();

      return ascending
        ? aText.localeCompare(bText)
        : bText.localeCompare(aText);
    });

    rows.forEach((row) => tbody.appendChild(row));
  });
});


document.querySelectorAll(".or-day-select").forEach(select => {

  function updateFilledState() {
    const td = select.closest("td");

    if (select.value.trim() !== "") {
      td.classList.add("filled-day");
    } else {
      td.classList.remove("filled-day");
    }
  }

  updateFilledState();

  select.addEventListener("change", updateFilledState);
});


const deleteBtn = document.getElementById("deleteCampaignBtn");

if (deleteBtn) {
  deleteBtn.addEventListener("click", () => {
    const campaignId = document.querySelector('[name="campaign_id"]').value;

    if (!campaignId) {
      alert("No campaign selected to delete.");
      return;
    }

    if (!confirm("Delete this campaign?")) {
      return;
    }

    const form = document.createElement("form");
    form.method = "POST";
    form.action = "/or-delete-campaign";

    const input = document.createElement("input");
    input.type = "hidden";
    input.name = "campaign_id";
    input.value = campaignId;

    form.appendChild(input);
    document.body.appendChild(form);
    form.submit();
  });
}

const daySelects = document.querySelectorAll(".or-day-select");

daySelects.forEach((select) => {
  select.addEventListener("change", async () => {
    const campaignId = select.dataset.campaignId;
    const date = select.dataset.date;
    const code = select.value;

    try {
      const response = await fetch("/or-save-day-code", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          campaign_id: campaignId,
          date: date,
          code: code,
        }),
      });

      if (!response.ok) {
        alert("Day code failed to save.");
      }
    } catch (error) {
      console.error("SAVE DAY CODE ERROR:", error);
      alert("Day code failed to save.");
    }
  });
});

const monthToggles = document.querySelectorAll(".month-toggle");

monthToggles.forEach((toggle) => {
  toggle.addEventListener("change", () => {
    const month = toggle.dataset.month;
    const isVisible = toggle.checked;

    const monthHeader = document.querySelector(`.month-header[data-month="${month}"]`);
    const monthCells = document.querySelectorAll(`.month-${month}`);

    if (monthHeader) {
      monthHeader.style.display = isVisible ? "" : "none";
    }

    monthCells.forEach((cell) => {
      cell.style.display = isVisible ? "" : "none";
    });
  });
});

const openUnitBtn = document.getElementById("openUnitModal");
const closeUnitBtn = document.getElementById("closeUnitModal");
const unitModal = document.getElementById("unitModal");

if (openUnitBtn && closeUnitBtn && unitModal) {
  openUnitBtn.addEventListener("click", () => {
    unitModal.classList.add("show");
  });

  closeUnitBtn.addEventListener("click", () => {
    unitModal.classList.remove("show");
  });

  unitModal.addEventListener("click", (event) => {
    if (event.target === unitModal) {
      unitModal.classList.remove("show");
    }
  });
}