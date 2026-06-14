/**
 * dashboard.js
 * ------------
 * Lightweight client-side helpers:
 * - pollTicketStatus(ticketId): polls /api/ticket/<id>/status every few
 *   seconds while a ticket is still being processed by the CrewAI crew,
 *   and reloads the page once the status changes to "Drafted" (or later).
 */

function pollTicketStatus(ticketId) {
    const inProgressStatuses = ["New", "Triaged", "Researched"];

    const interval = setInterval(async () => {
        try {
            const response = await fetch(`/api/ticket/${ticketId}/status`);
            if (!response.ok) return;

            const data = await response.json();

            if (!inProgressStatuses.includes(data.status)) {
                clearInterval(interval);
                // Reload the page to show the completed draft
                window.location.reload();
            }
        } catch (err) {
            console.error("Error polling ticket status:", err);
        }
    }, 4000); // poll every 4 seconds
}
