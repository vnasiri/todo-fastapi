/**
 * Utility Functions Module
 * Provides common utility functions used throughout the application
 */

/**
 * Show a toast notification
 * @param {string} message - The message to display
 * @param {string} type - The type of toast: 'success', 'danger', 'warning', 'info'
 * @param {number} duration - Duration in milliseconds (default: 5000)
 */
function showToast(message, type = "info", duration = 5000) {
  const toastContainer = document.getElementById("toastContainer");
  if (!toastContainer) {
    console.warn("Toast container not found");
    return;
  }

  const toastId = `toast-${Date.now()}`;
  const bgColorClass = `bg-${
    type === "success"
      ? "success"
      : type === "danger"
      ? "danger"
      : type === "warning"
      ? "warning"
      : "info"
  }`;

  const iconClass = `bi-${
    type === "success"
      ? "check-circle"
      : type === "danger"
      ? "exclamation-circle"
      : type === "warning"
      ? "exclamation-triangle"
      : "info-circle"
  }`;

  // Create toast elements safely
  const toastElement = document.createElement("div");
  toastElement.id = toastId;
  toastElement.className = "toast show";
  toastElement.setAttribute("role", "alert");
  toastElement.setAttribute("aria-live", "assertive");
  toastElement.setAttribute("aria-atomic", "true");

  const header = document.createElement("div");
  header.className = `toast-header ${bgColorClass} text-white`;

  const icon = document.createElement("i");
  icon.className = `bi ${iconClass} me-2`;

  const title = document.createElement("strong");
  title.className = "me-auto";
  title.textContent = capitalizeFirst(type);

  const closeBtn = document.createElement("button");
  closeBtn.type = "button";
  closeBtn.className = "btn-close btn-close-white";
  closeBtn.setAttribute("data-bs-dismiss", "toast");

  header.appendChild(icon);
  header.appendChild(title);
  header.appendChild(closeBtn);

  const body = document.createElement("div");
  body.className = "toast-body";
  body.textContent = message;

  toastElement.appendChild(header);
  toastElement.appendChild(body);
  toastContainer.appendChild(toastElement);

  const toast = new bootstrap.Toast(toastElement);
  toast.show();

  // Remove toast element after it's hidden
  toastElement.addEventListener("hidden.bs.toast", () => {
    toastElement.remove();
  });

  // Auto-hide after duration
  if (duration > 0) {
    setTimeout(() => {
      toast.hide();
    }, duration);
  }
}

/**
 * Capitalize first letter of a string
 */
function capitalizeFirst(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Format date to readable string
 */
function formatDate(date) {
  if (typeof date === "string") {
    date = new Date(date);
  }

  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

/**
 * Format date and time
 */
function formatDateTime(date) {
  if (typeof date === "string") {
    date = new Date(date);
  }

  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/**
 * Parse JWT token (without validation)
 */
function parseJWT(token) {
  try {
    const base64Url = token.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error("Error parsing JWT:", error);
    return null;
  }
}

/**
 * Check if user has a specific role
 */
function hasRole(role) {
  // This would typically check the JWT token or user data
  // For now, returning a placeholder
  return true;
}

/**
 * Debounce function
 */
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Throttle function
 */
function throttle(func, limit) {
  let inThrottle;
  return function (...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

/**
 * Deep clone object
 */
function deepClone(obj) {
  return JSON.parse(JSON.stringify(obj));
}

/**
 * Check if object is empty
 */
function isEmpty(obj) {
  return Object.keys(obj).length === 0;
}

/**
 * Merge objects
 */
function mergeObjects(target, source) {
  return { ...target, ...source };
}

/**
 * Get query parameter from URL
 */
function getQueryParam(param) {
  const searchParams = new URLSearchParams(window.location.search);
  return searchParams.get(param);
}

/**
 * Set multiple query parameters and update URL
 */
function setQueryParams(params) {
  const searchParams = new URLSearchParams(window.location.search);

  Object.keys(params).forEach((key) => {
    if (params[key] !== null && params[key] !== undefined) {
      searchParams.set(key, params[key]);
    } else {
      searchParams.delete(key);
    }
  });

  const newUrl = `${window.location.pathname}?${searchParams.toString()}`;
  window.history.replaceState({}, "", newUrl);
}

/**
 * Escape HTML special characters to prevent XSS
 */
function escapeHtml(text) {
  if (!text) return "";
  const map = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  };
  return String(text).replace(/[&<>"']/g, (char) => map[char]);
}

/**
 * Sanitize HTML (remove script tags and event handlers)
 */
function sanitizeHtml(html) {
  // Use the safe escapeHtml function to prevent XSS
  return escapeHtml(html);
}

/**
 * Validate email format
 */
function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validate password strength
 */
function validatePasswordStrength(password) {
  const strength = {
    hasMinLength: password.length >= 8,
    hasUpperCase: /[A-Z]/.test(password),
    hasLowerCase: /[a-z]/.test(password),
    hasNumbers: /\d/.test(password),
    hasSpecialChar: /[^a-zA-Z\d]/.test(password),
  };

  const score = Object.values(strength).filter(Boolean).length;

  return {
    strength,
    score,
    level: score < 2 ? "weak" : score < 4 ? "fair" : "strong",
  };
}

/**
 * Validate username format
 */
function isValidUsername(username) {
  // Username: 3-20 characters, alphanumeric and underscore only
  const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
  return usernameRegex.test(username);
}

/**
 * Format bytes to human-readable format
 */
function formatBytes(bytes) {
  if (bytes === 0) return "0 Bytes";

  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
}

/**
 * Sleep/delay function (async)
 */
async function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Get relative time string (e.g., "2 hours ago")
 */
function getRelativeTime(date) {
  if (typeof date === "string") {
    date = new Date(date);
  }

  const now = new Date();
  const diff = Math.floor((now - date) / 1000); // Difference in seconds

  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)} minutes ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} hours ago`;
  if (diff < 604800) return `${Math.floor(diff / 86400)} days ago`;

  return formatDate(date);
}

/**
 * Copy text to clipboard
 */
async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (error) {
    console.error("Failed to copy to clipboard:", error);
    return false;
  }
}

/**
 * Generate random ID
 */
function generateId() {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Limit string length with ellipsis
 */
function truncateString(str, maxLength = 50, ellipsis = "...") {
  if (str.length <= maxLength) return str;
  return str.substring(0, maxLength - ellipsis.length) + ellipsis;
}

/**
 * Convert seconds to human-readable time format
 */
function formatTime(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  const parts = [];
  if (hours > 0) parts.push(`${hours}h`);
  if (minutes > 0) parts.push(`${minutes}m`);
  if (secs > 0 || parts.length === 0) parts.push(`${secs}s`);

  return parts.join(" ");
}

/**
 * Request notification permission from user
 */
async function requestNotificationPermission() {
  if (!("Notification" in window)) {
    console.warn("Notifications not supported");
    return false;
  }

  if (Notification.permission === "granted") {
    return true;
  }

  if (Notification.permission !== "denied") {
    const permission = await Notification.requestPermission();
    return permission === "granted";
  }

  return false;
}

/**
 * Send browser notification
 */
function sendNotification(title, options = {}) {
  if (Notification.permission === "granted") {
    return new Notification(title, {
      icon: "/static/img/icon-192x192.png",
      ...options,
    });
  }
}
