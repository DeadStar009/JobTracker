const statusLog = document.getElementById("statusLog");
const actions = [
    "Job feed synchronized",
    "Application status changed",
    "Background sync completed",
    "Table re-indexed in 14ms",
    "Cache cleared successfully",
];

if (statusLog) {
    setInterval(() => {
        const action = actions[Math.floor(Math.random() * actions.length)];
        const now = new Date();
        const time = now.toLocaleTimeString([], { hour12: false });
        statusLog.textContent = `[System] ${action} — ${time}`;
    }, 15000);
}

const globalSearch = document.getElementById("globalSearch");
const statusFilter = document.getElementById("statusFilter");
const applicationsTable = document.getElementById("applicationsTable");
const urlParams = new URLSearchParams(window.location.search);
const initialQuery = urlParams.get("q");
if (globalSearch && initialQuery) {
    globalSearch.value = initialQuery;
}

function filterApplications() {
    if (!applicationsTable) {
        return;
    }

    const searchValue = (globalSearch?.value || "").toLowerCase();
    const statusValue = statusFilter?.value || "";
    const rows = applicationsTable.querySelectorAll("tbody tr");

    rows.forEach((row) => {
        const text = row.textContent.toLowerCase();
        const status = row.getAttribute("data-status") || "";
        const matchesSearch = !searchValue || text.includes(searchValue);
        const matchesStatus = !statusValue || status === statusValue;
        row.style.display = matchesSearch && matchesStatus ? "" : "none";
    });
}

if (globalSearch) {
    globalSearch.addEventListener("input", () => {
        if (applicationsTable) {
            filterApplications();
        }
    });
    globalSearch.addEventListener("keydown", (event) => {
        if (event.key !== "Enter") {
            return;
        }
        const query = globalSearch.value.trim();
        if (applicationsTable) {
            filterApplications();
            return;
        }
        window.location.href = `/applications?q=${encodeURIComponent(query)}`;
    });
}

if (statusFilter) {
    statusFilter.addEventListener("change", filterApplications);
}

if (applicationsTable) {
    filterApplications();
}

const modalMap = {
    entry: document.getElementById("entryModal"),
    settings: document.getElementById("settingsModal"),
};

function toggleModal(name, isOpen) {
    const modal = modalMap[name];
    if (!modal) {
        return;
    }
    if (isOpen) {
        modal.hidden = false;
        modal.setAttribute("aria-hidden", "false");
        document.body.style.overflow = "hidden";
        return;
    }
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    setTimeout(() => {
        modal.hidden = true;
    }, 200);
}

document.querySelectorAll("[data-modal-open]").forEach((button) => {
    button.addEventListener("click", () => {
        toggleModal(button.dataset.modalOpen, true);
    });
});

document.querySelectorAll("[data-modal-close]").forEach((button) => {
    button.addEventListener("click", () => {
        toggleModal(button.dataset.modalClose, false);
    });
});

document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") {
        return;
    }
    Object.keys(modalMap).forEach((name) => toggleModal(name, false));
    closeNotes();
});

const notesModal = document.getElementById("notesModal");
const notesTitle = document.getElementById("notesTitle");
const notesBody = document.getElementById("notesBody");
const detailsModal = document.getElementById("detailsModal");
const detailsTitle = document.getElementById("detailsTitle");
const detailsGrid = document.getElementById("detailsGrid");
const detailsNotes = document.getElementById("detailsNotes");

function openNotes(title, body) {
    if (!notesModal) {
        return;
    }
    notesModal.hidden = false;
    notesModal.setAttribute("aria-hidden", "false");
    if (notesTitle) {
        notesTitle.textContent = `[ NOTES: ${title || "ENTRY"} ]`;
    }
    if (notesBody) {
        notesBody.textContent = body || "No notes available.";
    }
    document.body.style.overflow = "hidden";
}

function closeNotes() {
    if (!notesModal) {
        return;
    }
    notesModal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    setTimeout(() => {
        notesModal.hidden = true;
    }, 200);
}

document.querySelectorAll("[data-notes]").forEach((button) => {
    button.addEventListener("click", () => {
        openNotes(button.dataset.notesTitle, button.dataset.notes);
    });
});

document.querySelectorAll("[data-notes-close]").forEach((button) => {
    button.addEventListener("click", () => {
        closeNotes();
    });
});

function openDetails(data) {
    if (!detailsModal || !detailsGrid) {
        return;
    }
    closeNotes();
    detailsModal.hidden = false;
    detailsModal.setAttribute("aria-hidden", "false");
    if (detailsTitle) {
        detailsTitle.textContent = `[ ENTRY: ${data.company || data.id || "DETAILS"} ]`;
    }
    const rows = [
        ["ID_KEY", data.id, "label-id"],
        ["COMPANY", data.company, "label-company"],
        ["ROLE", data.role, "label-role"],
        ["LOCATION", data.location, "label-location"],
        ["DATE_ADDED", data.date, "label-date"],
        ["DAYS_SINCE", data.days ? `${data.days}d` : "", "label-days"],
        ["STATUS", data.status, "label-status"],
        ["PRIORITY", data.color ? data.color.toUpperCase() : "NONE", "label-color"],
        ["SALARY", data.salary, "label-salary"],
    ];
    detailsGrid.innerHTML = rows
        .map(
            ([label, value, labelClass]) => `
                <div class="details-row">
                    <span class="details-label ${labelClass}">${label}</span>
                    <span class="details-value">${value || "-"}</span>
                </div>
            `
        )
        .join("");
    if (detailsNotes) {
        detailsNotes.textContent = data.notes || "No notes available.";
    }
    document.body.style.overflow = "hidden";
}

function closeDetails() {
    if (!detailsModal) {
        return;
    }
    detailsModal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    setTimeout(() => {
        detailsModal.hidden = true;
    }, 200);
    closeNotes();
}

document.querySelectorAll("[data-details]").forEach((row) => {
    row.addEventListener("click", (event) => {
        const target = event.target;
        if (target && target.closest("[data-stop-row]")) {
            return;
        }
        openDetails({
            id: row.dataset.id,
            company: row.dataset.company,
            role: row.dataset.role,
            location: row.dataset.location,
            date: row.dataset.date,
            days: row.dataset.days,
            status: row.dataset.statusValue || row.dataset.status,
            salary: row.dataset.salary,
            color: row.dataset.color,
            notes: row.dataset.notes,
        });
    });
});

document.querySelectorAll("[data-details-close]").forEach((button) => {
    button.addEventListener("click", () => {
        closeDetails();
    });
});

// Window controls for desktop app
function minimizeWindow() {
    if (window.pywebview) {
        window.pywebview.api.minimize_window();
    }
}

function closeWindow() {
    if (window.pywebview) {
        window.pywebview.api.close_window();
    } else {
        window.close();
    }
}

// Link handling for external URLs
document.addEventListener('click', function(e) {
    const link = e.target.closest('a[href^="http"]');
    if (link && window.pywebview) {
        e.preventDefault();
        window.pywebview.api.open_url(link.href);
    }
});
