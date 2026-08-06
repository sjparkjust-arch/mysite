"use strict";

document.addEventListener("DOMContentLoaded", () => {
    initializeMobileMenu();
    initializeAlertClose();
    initializePasswordToggle();
});


function initializeMobileMenu() {
    const button = document.querySelector("#mobile-menu-button");
    const menu = document.querySelector(".main-nav");

    if (!button || !menu) {
        return;
    }

    button.addEventListener("click", () => {
        const isOpen = menu.classList.toggle("open");

        button.setAttribute("aria-expanded", String(isOpen));
        button.textContent = isOpen ? "×" : "☰";
    });
}


function initializeAlertClose() {
    document.querySelectorAll(".alert-close").forEach((button) => {
        button.addEventListener("click", () => {
            button.closest(".alert")?.remove();
        });
    });
}


function initializePasswordToggle() {
    document.querySelectorAll(".password-toggle").forEach((button) => {
        button.addEventListener("click", () => {
            const targetId = button.dataset.target;
            const input = document.getElementById(targetId);

            if (!input) {
                return;
            }

            const showPassword = input.type === "password";

            input.type = showPassword ? "text" : "password";
            button.textContent = showPassword ? "숨김" : "보기";
        });
    });
}


function initializePostForm() {
    const titleInput = document.querySelector("#title");
    const titleCount = document.querySelector("#title-count");

    const fileInput = document.querySelector("#files");
    const selectButton = document.querySelector("#file-select-button");
    const dropZone = document.querySelector("#file-drop-zone");
    const selectedFileList = document.querySelector("#selected-file-list");

    if (titleInput && titleCount) {
        const updateTitleCount = () => {
            titleCount.textContent = `${titleInput.value.length} / 100`;
        };

        titleInput.addEventListener("input", updateTitleCount);
        updateTitleCount();
    }

    if (!fileInput || !selectButton || !dropZone || !selectedFileList) {
        return;
    }

    selectButton.addEventListener("click", () => {
        fileInput.click();
    });

    fileInput.addEventListener("change", () => {
        renderSelectedFiles(fileInput.files, selectedFileList);
    });

    ["dragenter", "dragover"].forEach((eventName) => {
        dropZone.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropZone.classList.add("drag-over");
        });
    });

    ["dragleave", "drop"].forEach((eventName) => {
        dropZone.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropZone.classList.remove("drag-over");
        });
    });

    dropZone.addEventListener("drop", (event) => {
        const files = event.dataTransfer.files;

        if (!files.length) {
            return;
        }

        const transfer = new DataTransfer();

        Array.from(files).forEach((file) => {
            transfer.items.add(file);
        });

        fileInput.files = transfer.files;

        renderSelectedFiles(fileInput.files, selectedFileList);
    });
}


function renderSelectedFiles(files, container) {
    container.innerHTML = "";

    Array.from(files).forEach((file) => {
        const item = document.createElement("div");

        item.className = "selected-file-item";

        item.innerHTML = `
            <span>📄 ${escapeHtml(file.name)}</span>
            <span>${formatFileSize(file.size)}</span>
        `;

        container.appendChild(item);
    });
}


function formatFileSize(bytes) {
    if (bytes === 0) {
        return "0 B";
    }

    const units = ["B", "KB", "MB", "GB"];
    const unitIndex = Math.floor(Math.log(bytes) / Math.log(1024));
    const size = bytes / Math.pow(1024, unitIndex);

    return `${size.toFixed(1)} ${units[unitIndex]}`;
}


function escapeHtml(value) {
    const element = document.createElement("div");

    element.textContent = value;

    return element.innerHTML;
}
